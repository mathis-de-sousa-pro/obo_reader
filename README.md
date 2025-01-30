# 🧩 KNIME OBO Reader Extension

## 📖 Description

The **KNIME OBO Reader Extension** is a custom KNIME node that enables users to read and process OBO (Ontology) files efficiently. It leverages `obonet`, `polars`, and `networkx` to extract nodes and edges from ontology files and convert them into KNIME-compatible tables.

This extension allows users to:
- Browse and select `.obo` files for parsing.
- Automatically detect available columns or manually specify them.
- Process and transform ontology data into tabular format.

---
## 🚀 Features

✅ **OBO File Selection:** Browse and select files instead of manually entering paths.  
✅ **Automatic Column Detection:** Choose to auto-detect columns or specify them manually.  
✅ **Node & Edge Extraction:** Extracts ontology terms as nodes and relationships as edges.  
✅ **Flexible Schema:** Supports different OBO structures dynamically.  

---
## 📌 Usage Instructions


### 🎯 **Adding the Node**

- Open KNIME and navigate to the `Community` section.
- Drag & drop **OBO NetworkX Reader** into your workflow.

---
### 🏗 **Configuration**

1. **Select the OBO file** using the Browse button.
2. **Choose column detection mode**:
    - 🔍 **Automatic:** Detects all available columns.
    - 📝 **Manual:** Allows specifying columns (e.g., `id, name, synonym`).
3. **Run the node** to extract data into two KNIME tables:
    - **Nodes Table** (`id`, `name`, `synonym`, `xref`, etc.).
    - **Edges Table** (`source`, `target`, `type`).

---
## 🤝 Contributing

We welcome contributions! Feel free to:

- 🛠 Improve the node functionality.
- 🐞 Report issues in the [GitHub Issues](https://github.com/mathis-de-sousa-pro/obo_reader/issues).
- 📖 Improve documentation.

---
## 🏆 Credits

Developed by **De Sousa Mathis** at **CIAD**.  
Special thanks to the KNIME community, especially **Martin from the KNIME forum**, for guidance!

---