import knime.extension as knext
import logging
import os
import obonet
import polars as pl
import pandas as pd
from networkx import to_pandas_edgelist

LOGGER = logging.getLogger(__name__)

# --- Define the category ---
my_category = knext.category(
    path="/community",
    level_id="obo_reader",
    name="OBO Reader",
    description="Nodes to read OBO files via obonet and polars",
    icon="icons/obo_icon.png"
)

class ColumnDetectionOptions(knext.EnumParameterOptions):
    AUTO = ("Automatic", "Automatically detect all columns from the OBO file.")
    MANUAL = ("Manual", "Specify the columns to extract manually.")

@knext.node(
    name="OBO Reader",
    node_type=knext.NodeType.SOURCE,
    icon_path="icons/obo_icon.png",
    category=my_category
)
@knext.output_table(
    name="Nodes Table",
    description="Table of extracted nodes (id, name, synonym, xref, etc.)."
)
@knext.output_table(
    name="Edges Table",
    description="Table of extracted edges (source, target, type, etc.)."
)
class OboNetReaderNode:
    """
    Reads an OBO file via obonet (NetworkX).
    Produces:
     - a table for nodes (with columns: id, name, synonym, xref, etc.)
     - a table for edges (edge list, with the column 'type')
    """

    # LocalPathParameter for file browsing
    obo_file = knext.LocalPathParameter(
        label="OBO File Path",
        description="Browse for a .obo file"
    )

    @obo_file.validator
    def validate_obo_file(path: str):
        if not path.lower().endswith(".obo"):
            raise ValueError("Please select a file with the '.obo' extension.")

    # Let the user pick how columns are determined
    column_detection = knext.EnumParameter(
        label="Column Detection Mode",
        description="Choose how columns are extracted",
        default_value=ColumnDetectionOptions.AUTO.name,
        enum=ColumnDetectionOptions
    )

    # If user chooses manual columns, we let them specify a comma-separated list
    columns_str = knext.StringParameter(
        label="Manual Columns",
        description="Comma-separated list of columns to extract if 'Manual' is selected above",
        default_value="id,name,synonym,xref",
        is_advanced=False
    #   -------------- VISIBILITY RULE -------------- 
    # We disable this field if 'column_detection' is set to "AUTO"
    ).rule(
        knext.OneOf(column_detection, [ColumnDetectionOptions.AUTO.name]),
        knext.Effect.DISABLE
    )

    def configure(self, config_context):
        # We let the node discover its schema dynamically, so no fixed schema here.
        return (None, None)

    def execute(self, exec_context):
        if not self.obo_file:
            raise ValueError("Please specify a valid OBO file path.")

        file_path = self.obo_file
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The specified OBO file was not found: {file_path}")

        # --- Read OBO via obonet ---
        nx_obo = obonet.read_obo(file_path)

        # Build the node data
        nodes_data = []
        for node_id, attrs in nx_obo.nodes(data=True):
            node_entry = {'id': node_id}
            node_entry.update(attrs)
            nodes_data.append(node_entry)

        # Convert to pandas -> polars
        nodes_df = pd.DataFrame(nodes_data)
        nodes_pl = pl.DataFrame(nodes_df)

        # *** 1) Automatic detection ***
        if self.column_detection == ColumnDetectionOptions.AUTO.name:
            # Keep all columns
            pass

        # *** 2) Manual specification ***
        else:
            desired_cols = [c.strip() for c in self.columns_str.split(",")]
            # Ensure 'id' is present
            if "id" not in desired_cols:
                desired_cols.insert(0, "id")

            existing_cols = set(nodes_pl.columns)
            # Create any missing columns if needed
            for c in desired_cols:
                if c not in existing_cols:
                    nodes_pl = nodes_pl.with_columns(pl.lit(None).alias(c))

            # Reorder/select only desired columns
            nodes_pl = nodes_pl.select(desired_cols)

        # Convert any list-like columns into semicolon-separated strings
        for col in nodes_pl.columns:
            if nodes_pl.schema[col] == pl.datatypes.Object:
                nodes_pl = nodes_pl.with_columns(
                    pl.col(col).apply(lambda v: "; ".join(v) if isinstance(v, list) else str(v) if v else "")
                )

        # Convert back to pandas
        nodes_pandas = nodes_pl.to_pandas()

        # Extract edge attributes
        edges_df = to_pandas_edgelist(nx_obo, edge_key="type")
        edges_pl = pl.DataFrame(edges_df)
        edges_pandas = edges_pl.to_pandas()

        # Create KNIME tables
        knime_nodes_table = knext.Table.from_pandas(nodes_pandas)
        knime_edges_table = knext.Table.from_pandas(edges_pandas)

        return (knime_nodes_table, knime_edges_table)
