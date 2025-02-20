document.addEventListener("DOMContentLoaded", function () {
  // Al caricamento della pagina, cancello i dati delle sessioni precedenti
  sessionStorage.removeItem("e2oData");
  sessionStorage.removeItem("o2oData");

  // Variabile per la larghezza fissa dei selettori (modificabile in un'unica soluzione)
  const SELECTOR_WIDTH = "w-64";

  // Dichiarazioni per aggiornamenti dinamici dopo la creazione dell'OCEL.
  let availableTypes = ["txHash", "inputs_inputName", "sender", "contractAddress", "gasUsed", "activity"];
  let availableActivities = ["approve", "sendFrom", "transfer"];

  const fileInput = document.getElementById("fileInput");
  const startMappingBtn = document.getElementById("startMappingBtn");
  const sampleBtn = document.getElementById("sampleBtn");
  const preview = document.getElementById("preview");
  const mappingPage = document.getElementById("mappingPage");

  // ---------------- Persistence Functions ----------------

  // Per E2O (qualifierPage)
  function saveE2OData() {
    const container = document.getElementById("qualifierContainer");
    let rows = container.getElementsByClassName("qualifier-row");
    let data = [];
    Array.from(rows).forEach(row => {
      let type = row.querySelector(".ocel-type-select").value;
      let activity = row.querySelector(".ocel-activity-select").value;
      let qualifier = row.querySelector(".qualifier-input").value;
      data.push({ type, activity, qualifier });
    });
    sessionStorage.setItem("e2oData", JSON.stringify(data));
  }

  function loadE2OData() {
    let data = sessionStorage.getItem("e2oData");
    return data ? JSON.parse(data) : null;
  }

  // Per O2O (o2oPage)
  function saveO2OData() {
    const container = document.getElementById("o2oContainer");
    let rows = container.getElementsByClassName("o2o-qualifier-row");
    let data = [];
    Array.from(rows).forEach(row => {
      let source = row.querySelector(".ocel-oid-select").value;
      let target = row.querySelector(".ocel-oid2-select").value;
      let qualifier = row.querySelector(".o2o-qualifier-input").value;
      data.push({ source, target, qualifier });
    });
    sessionStorage.setItem("o2oData", JSON.stringify(data));
  }

  function loadO2OData() {
    let data = sessionStorage.getItem("o2oData");
    return data ? JSON.parse(data) : null;
  }

  // ---------------- File Upload / Sample ----------------

  fileInput.addEventListener("change", async function () {
    if (this.files.length) {
      const formData = new FormData();
      formData.append("file", this.files[0]);
      try {
        const uploadResponse = await fetch("/upload", {
          method: "POST",
          body: formData,
        });
        if (!uploadResponse.ok) throw new Error("Upload failed");
        const previewResponse = await fetch("/preview");
        if (!previewResponse.ok) throw new Error("Preview failed");
        const previewData = await previewResponse.json();
        displayData(previewData);
        startMappingBtn.disabled = false;
      } catch (error) {
        console.error("Error:", error);
        alert(error.message);
      }
    }
  });

  sampleBtn.addEventListener("click", async function () {
    try {
      const response = await fetch("/static/pancacke100txs.json?cacheBust=" + Date.now());
      if (!response.ok) throw new Error("Failed to load sample");
      const data = await response.json();
      displayData(data);
      startMappingBtn.disabled = false;
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while loading the sample file");
    }
  });

  // ---------------- Helper Functions ----------------

  function getSchemaFromObject(obj) {
    const schema = {};
    Object.keys(obj).forEach(key => {
      const val = obj[key];
      if (Array.isArray(val)) {
        schema[key] = val.length > 0 ? [getSchemaFromObject(val[0])] : [];
      } else if (typeof val === "object" && val !== null) {
        schema[key] = getSchemaFromObject(val);
      } else {
        schema[key] = "";
      }
    });
    return schema;
  }

  function displayData(data) {
    let columns, sampleData, nestedColumns;
    if (data.preview_columns && data.sample_data) {
      columns = data.preview_columns;
      sampleData = data.sample_data;
      nestedColumns = data.nested_columns || [];
    } else if (data.columns && data.sample_data) {
      columns = data.columns;
      sampleData = data.sample_data;
      nestedColumns = data.nested_columns || [];
    } else if (Array.isArray(data)) {
      columns = Object.keys(data[0] || {});
      sampleData = data;
      nestedColumns = [];
    } else {
      throw new Error("Data structure not recognized");
    }
    const firstRecord = sampleData[0] || {};
    const schema = getSchemaFromObject(firstRecord);
    preview.innerHTML = "";
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(schema, null, 2);
    preview.appendChild(pre);
    // Aggiorna il select "Columns to Normalize"
    const columnsToNormalize = document.getElementById("columnsToNormalize");
    columnsToNormalize.innerHTML = "";
    nestedColumns.forEach((column, index) => {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = column;
      columnsToNormalize.appendChild(option);
    });
    preview.classList.remove("hidden");
  }

  // ---------------- Mapping Page ----------------

  function setupMappingPage(previewData) {
    const columnsToNormalize = document.getElementById("columnsToNormalize");
    columnsToNormalize.innerHTML = "";
    previewData.nested_columns.forEach((col, index) => {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = col;
      columnsToNormalize.appendChild(option);
    });
    $("#columnsToNormalize").select2({
      placeholder: "Select columns to normalize",
      allowClear: true,
      width: "100%",
      selectionCssClass: "border-gray-300",
      dropdownCssClass: "border-gray-300",
      closeOnSelect: false,
    });
    const table = document.querySelector("#mappingPage table");
    const thead = table.querySelector("thead tr");
    const tbody = table.querySelector("tbody");
    thead.innerHTML = "";
    tbody.innerHTML = "";
    previewData.preview_columns.forEach(col => {
      const th = document.createElement("th");
      th.textContent = col;
      th.className = "px-4 py-2 bg-gray-100 sticky top-0";
      thead.appendChild(th);
    });
    previewData.sample_data.slice(0, 10).forEach(row => {
      const tr = document.createElement("tr");
      previewData.preview_columns.forEach(col => {
        const td = document.createElement("td");
        let content = row[col];
        if (typeof content === "object") {
          content = JSON.stringify(content, null, 2);
        }
        td.textContent = content;
        td.className = "px-4 py-2 border whitespace-nowrap";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    document.getElementById("backBtn").addEventListener("click", () => {
      mappingPage.classList.add("hidden");
      document.getElementById("results").classList.remove("hidden");
    });
    document.getElementById("continueBtn").addEventListener("click", async () => {
      const selectedOptions = Array.from(columnsToNormalize.selectedOptions);
      const indexes = selectedOptions.map(opt => parseInt(opt.value));
      try {
        const response = await fetch("/normalize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ indexes })
        });
        if (!response.ok) throw new Error("Normalization failed");
        const result = await response.json();
        console.log(result.message);
        mappingPage.classList.add("hidden");
        setupSelectionPage(result.columns);
      } catch (error) {
        console.error("Error:", error);
        alert(error.message);
      }
    });

    // Popola la pagina Select Attributes.
    function setupSelectionPage(columns) {
      const selectionPage = document.getElementById("selectionPage");
      selectionPage.classList.remove("hidden");
      const activitySelect = document.getElementById("activitySelect");
      const timestampSelect = document.getElementById("timestampSelect");
      const objectTypesSelect = document.getElementById("objectTypesSelect");
      const additionalEventAttributesSelect = document.getElementById("additionalEventAttributesSelect");
      [activitySelect, timestampSelect, objectTypesSelect, additionalEventAttributesSelect].forEach(select => {
        select.innerHTML = "";
      });
      columns.forEach(col => {
        let option = document.createElement("option");
        option.value = col;
        option.textContent = col;
        if (col.toLowerCase() === "activity") option.selected = true;
        activitySelect.appendChild(option.cloneNode(true));
        option = document.createElement("option");
        option.value = col;
        option.textContent = col;
        if (col.toLowerCase() === "timestamp") option.selected = true;
        timestampSelect.appendChild(option.cloneNode(true));
        option = document.createElement("option");
        option.value = col;
        option.textContent = col;
        objectTypesSelect.appendChild(option.cloneNode(true));
        additionalEventAttributesSelect.appendChild(option.cloneNode(true));
      });
      $("#objectTypesSelect").select2({
        placeholder: "Select objects",
        allowClear: true,
        width: "100%",
        closeOnSelect: false,
      });
      $("#additionalEventAttributesSelect").select2({
        placeholder: "Select event attributes",
        allowClear: true,
        width: "100%",
        closeOnSelect: false,
      });
      const container = document.getElementById("objectTypeAttributesContainer");
      container.innerHTML = "";
      $(objectTypesSelect).on("change", function () {
        updateObjectTypeAttributesContainer(columns);
      });
      document.getElementById("finalizeBtn").addEventListener("click", async function () {
        const activity = activitySelect.value;
        const timestamp = timestampSelect.value;
        const object_types = Array.from(objectTypesSelect.selectedOptions).map(opt => opt.value);
        const events_attrs = Array.from(additionalEventAttributesSelect.selectedOptions).map(opt => opt.value);
        const container = document.getElementById("objectTypeAttributesContainer");
        let object_attrs = {};
        Array.from(container.children).forEach(child => {
          const objType = child.id.replace("objectType_", "");
          const select = child.querySelector("select");
          const attrs = Array.from(select.selectedOptions).map(opt => opt.value);
          object_attrs[objType] = [objType, ...attrs];
        });
        try {
          const response = await fetch("/set_ocel_parameters", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              activity,
              timestamp,
              object_types,
              events_attrs,
              object_attrs
            })
          });
          if (!response.ok) throw new Error("Setting OCEL parameters failed");
          const result = await response.json();
          console.log(result.message);
          // Aggiorna i qualificatori dinamici con quelli ricevuti dal backend.
          availableTypes = result.available_types;
          availableActivities = result.available_activities;
          document.getElementById("selectionPage").classList.add("hidden");
          document.getElementById("qualifierPage").classList.remove("hidden");
          initializeQualifierRows();
        } catch (error) {
          console.error("Error:", error);
          alert(error.message);
        }
      });
    }
  }

  function updateObjectTypeAttributesContainer(columns) {
    const objectTypesSelect = document.getElementById("objectTypesSelect");
    const container = document.getElementById("objectTypeAttributesContainer");
    const selectedObjectTypes = Array.from(objectTypesSelect.selectedOptions).map(opt => opt.value);
    selectedObjectTypes.forEach(type => {
      if (!document.getElementById("objectType_" + type)) {
        const div = document.createElement("div");
        div.id = "objectType_" + type;
        div.className = "mb-2";
        const label = document.createElement("label");
        label.textContent = type + " Attributes:";
        label.className = "block text-sm font-medium text-gray-700 mb-1";
        const select = document.createElement("select");
        select.multiple = true;
        select.className = "w-full p-2 border rounded object-attributes-select";
        columns.forEach(col => {
          const option = document.createElement("option");
          option.value = col;
          option.textContent = col;
          select.appendChild(option);
        });
        div.appendChild(label);
        div.appendChild(select);
        container.appendChild(div);
        $(select).select2({
          placeholder: "Select attributes",
          allowClear: true,
          width: "100%",
          closeOnSelect: false,
        });
      }
    });
    Array.from(container.children).forEach(child => {
      const type = child.id.replace("objectType_", "");
      if (!selectedObjectTypes.includes(type)) {
        container.removeChild(child);
      }
    });
  }

  // ---------------- QUALIFIER PAGE (E2O) ----------------

  function initializeQualifierRows() {
    const container = document.getElementById("qualifierContainer");
    container.innerHTML = "";

    // Header per E2O
    const headerRow = document.createElement("div");
    headerRow.className = "qualifier-header flex space-x-2 mb-2 font-bold";
    const headerObjTypes = document.createElement("div");
    headerObjTypes.textContent = "Object Types";
    headerObjTypes.className = `${SELECTOR_WIDTH} text-center`;
    const headerEvtTypes = document.createElement("div");
    headerEvtTypes.textContent = "Event Types";
    headerEvtTypes.className = `${SELECTOR_WIDTH} text-center`;
    const headerQualifier = document.createElement("div");
    headerQualifier.textContent = "Relationship qualifier";
    headerQualifier.className = `${SELECTOR_WIDTH} text-center`;
    const headerDelete = document.createElement("div");
    headerDelete.className = "w-8";
    headerRow.appendChild(headerObjTypes);
    headerRow.appendChild(headerEvtTypes);
    headerRow.appendChild(headerQualifier);
    headerRow.appendChild(headerDelete);
    container.appendChild(headerRow);

    let savedData = loadE2OData();
    if (savedData && savedData.length > 0) {
      savedData.forEach(item => addQualifierRow(item));
    } else {
      addQualifierRow();
    }
  }

  function addQualifierRow(savedItem) {
    const container = document.getElementById("qualifierContainer");
    const rowDiv = document.createElement("div");
    rowDiv.className = "qualifier-row mb-2 flex space-x-2 items-center";

    const typeSelect = document.createElement("select");
    typeSelect.className = "ocel-type-select p-2 border rounded " + SELECTOR_WIDTH;
    availableTypes.forEach(type => {
      const option = document.createElement("option");
      option.value = type;
      option.textContent = type;
      typeSelect.appendChild(option);
    });

    const activitySelect = document.createElement("select");
    activitySelect.className = "ocel-activity-select p-2 border rounded " + SELECTOR_WIDTH;
    availableActivities.forEach(act => {
      const option = document.createElement("option");
      option.value = act;
      option.textContent = act;
      activitySelect.appendChild(option);
    });

    const qualifierInput = document.createElement("input");
    qualifierInput.type = "text";
    qualifierInput.placeholder = "Enter qualifier";
    qualifierInput.className = "qualifier-input p-2 border rounded " + SELECTOR_WIDTH;

    if (savedItem) {
      typeSelect.value = savedItem.type;
      activitySelect.value = savedItem.activity;
      qualifierInput.value = savedItem.qualifier;
    }

    [typeSelect, activitySelect, qualifierInput].forEach(el => {
      el.addEventListener("change", saveE2OData);
      el.addEventListener("input", saveE2OData);
    });

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "X";
    deleteButton.className = "delete-row-button p-2 bg-red-500 text-white rounded";
    deleteButton.addEventListener("click", function() {
      rowDiv.remove();
      saveE2OData();
    });

    rowDiv.appendChild(typeSelect);
    rowDiv.appendChild(activitySelect);
    rowDiv.appendChild(qualifierInput);
    rowDiv.appendChild(deleteButton);

    container.appendChild(rowDiv);

    qualifierInput.addEventListener("input", function () {
      const rows = container.getElementsByClassName("qualifier-row");
      if (rows[rows.length - 1] === rowDiv && qualifierInput.value.trim() !== "") {
        addQualifierRow();
      }
      saveE2OData();
    });
  }

  // ---------------- QUALIFIER PAGE (O2O) ----------------

  async function initializeO2OQualifierRows() {
    const container = document.getElementById("o2oContainer");
    container.innerHTML = "";

    // Header per O2O
    const headerRow = document.createElement("div");
    headerRow.className = "o2o-header flex items-center space-x-2 mb-2 font-bold";
    const headerSource = document.createElement("div");
    headerSource.textContent = "Object Source";
    headerSource.className = `${SELECTOR_WIDTH} text-center`;
    const headerTarget = document.createElement("div");
    headerTarget.textContent = "Object Target";
    headerTarget.className = `${SELECTOR_WIDTH} text-center`;
    const headerQualifier = document.createElement("div");
    headerQualifier.textContent = "Relationship Qualifier";
    headerQualifier.className = `${SELECTOR_WIDTH} text-center`;
    const headerDelete = document.createElement("div");
    headerDelete.className = "w-8";
    headerRow.appendChild(headerSource);
    headerRow.appendChild(headerTarget);
    headerRow.appendChild(headerQualifier);
    headerRow.appendChild(headerDelete);
    container.appendChild(headerRow);

    let savedData = loadO2OData();
    if (savedData && savedData.length > 0) {
      savedData.forEach(item => addO2OQualifierRow(item));
    } else {
      fetchO2OObjects();
    }
  }

  function fetchO2OObjects() {
    fetch("/get_o2o_objects")
      .then(response => {
        if (!response.ok) throw new Error("Errore nel recupero degli oggetti O2O");
        return response.json();
      })
      .then(data => {
        const oids = data.oids || [];
        const oids_2 = data.oids_2 || [];
        addO2OQualifierRow(oids, oids_2);
      })
      .catch(error => {
        console.error("Errore:", error);
        alert(error.message);
      });
  }

  // La funzione addO2OQualifierRow accetta un parametro opzionale "savedItem".
  // Se passato, viene ripristinato il valore salvato; altrimenti usa i parametri oids e oids_2.
  function addO2OQualifierRow(param1, param2OrSaved) {
    const container = document.getElementById("o2oContainer");
    const rowDiv = document.createElement("div");
    rowDiv.className = "o2o-qualifier-row flex items-center space-x-2 mb-2";
    let oids, oids_2, savedItem;
    if (typeof param2OrSaved === "object" && param2OrSaved.source !== undefined) {
      savedItem = param2OrSaved;
      oids = window.currentOids || [];
      oids_2 = window.currentOids2 || [];
    } else {
      oids = param1;
      oids_2 = param2OrSaved;
      window.currentOids = oids;
      window.currentOids2 = oids_2;
    }
    const sourceSelect = document.createElement("select");
    sourceSelect.className = "ocel-oid-select p-2 border rounded " + SELECTOR_WIDTH;
    oids.forEach(oid => {
      const option = document.createElement("option");
      option.value = oid;
      option.textContent = oid;
      sourceSelect.appendChild(option);
    });
    const targetSelect = document.createElement("select");
    targetSelect.className = "ocel-oid2-select p-2 border rounded " + SELECTOR_WIDTH;
    oids_2.forEach(oid2 => {
      const option = document.createElement("option");
      option.value = oid2;
      option.textContent = oid2;
      targetSelect.appendChild(option);
    });
    const qualifierInput = document.createElement("input");
    qualifierInput.type = "text";
    qualifierInput.placeholder = "Enter qualifier";
    qualifierInput.className = "o2o-qualifier-input p-2 border rounded " + SELECTOR_WIDTH;
    if (savedItem) {
      sourceSelect.value = savedItem.source;
      targetSelect.value = savedItem.target;
      qualifierInput.value = savedItem.qualifier;
    }
    [sourceSelect, targetSelect, qualifierInput].forEach(el => {
      el.addEventListener("change", saveO2OData);
      el.addEventListener("input", saveO2OData);
    });
    const deleteButton = document.createElement("button");
    deleteButton.textContent = "X";
    deleteButton.className = "delete-row-button p-2 bg-red-500 text-white rounded";
    deleteButton.addEventListener("click", function() {
      rowDiv.remove();
      saveO2OData();
    });
    const deleteButtonContainer = document.createElement("div");
    deleteButtonContainer.className = "w-8";
    deleteButtonContainer.appendChild(deleteButton);
    rowDiv.appendChild(sourceSelect);
    rowDiv.appendChild(targetSelect);
    rowDiv.appendChild(qualifierInput);
    rowDiv.appendChild(deleteButtonContainer);
    container.appendChild(rowDiv);
    qualifierInput.addEventListener("input", function() {
      const rows = container.getElementsByClassName("o2o-qualifier-row");
      if (rows[rows.length - 1] === rowDiv && qualifierInput.value.trim() !== "") {
        addO2OQualifierRow(oids, oids_2);
      }
      saveO2OData();
    });
  }

  // ---------------- Bottoni e Navigazione ----------------

  document.getElementById("submitQualificationsBtn").addEventListener("click", async function () {
    // Salva i dati E2O prima di inviare
    saveE2OData();
    try {
      const response = await fetch("/set_e2o_relationship_qualifiers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qualifier_map: buildE2OQualifierMap() })
      });
      if (!response.ok) throw new Error("Errore nella configurazione di E2O");
      const result = await response.json();
      console.log(result.message);
      // Naviga alla pagina O2O
      document.getElementById("qualifierPage").classList.add("hidden");
      document.getElementById("o2oPage").classList.remove("hidden");
      // Se non ci sono già dati salvati per O2O, inizializza la pagina O2O.
      const savedO2O = loadO2OData();
      if (!savedO2O || savedO2O.length === 0) {
        initializeO2OQualifierRows();
      }
    } catch (error) {
      console.error("Errore:", error);
      alert(error.message);
    }
  });

  function buildE2OQualifierMap() {
    const container = document.getElementById("qualifierContainer");
    const rows = container.getElementsByClassName("qualifier-row");
    let qualifierMap = {};
    Array.from(rows).forEach(row => {
      const type = row.querySelector(".ocel-type-select").value;
      const activity = row.querySelector(".ocel-activity-select").value;
      const qualifier = row.querySelector(".qualifier-input").value.trim();
      if (qualifier !== "") {
        qualifierMap[`${type}|${activity}`] = qualifier;
      }
    });
    return qualifierMap;
  }

  document.getElementById("exportO2OBtn").addEventListener("click", async function () {
    saveO2OData();
    try {
      const response = await fetch("/set_o2o_relationship_qualifiers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qualifier_map: buildO2OQualifierMap() })
      });
      if (!response.ok) throw new Error("Errore nella configurazione di O2O");
      const result = await response.json();
      console.log(result.message);
    } catch (error) {
      console.error("Errore:", error);
      alert(error.message);
    }
  });

  function buildO2OQualifierMap() {
    const container = document.getElementById("o2oContainer");
    const rows = container.getElementsByClassName("o2o-qualifier-row");
    let qualifierMap = {};
    Array.from(rows).forEach(row => {
      const oid = row.querySelector(".ocel-oid-select").value;
      const oid2 = row.querySelector(".ocel-oid2-select").value;
      const qualifier = row.querySelector(".o2o-qualifier-input").value.trim();
      if (qualifier !== "") {
        qualifierMap[`${oid}|${oid2}`] = qualifier;
      }
    });
    return qualifierMap;
  }

  document.getElementById("backFromO2OBtn").addEventListener("click", function () {
    // Salva i dati O2O prima di tornare
    saveO2OData();
    document.getElementById("o2oPage").classList.add("hidden");
    document.getElementById("qualifierPage").classList.remove("hidden");
  });

  document.getElementById("backFromQualifierBtn").addEventListener("click", function () {
    // Naviga indietro dalla pagina qualifier senza cancellare i dati salvati
    document.getElementById("qualifierPage").classList.add("hidden");
    document.getElementById("selectionPage").classList.remove("hidden");
  });

  startMappingBtn.addEventListener("click", async function () {
    try {
      const response = await fetch("/preview");
      if (!response.ok) throw new Error("Preview failed");
      const previewData = await response.json();
      setupMappingPage(previewData);
      mappingPage.classList.remove("hidden");
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to load preview data");
    }
  });

  document.getElementById("backBtn").addEventListener("click", function () {
    mappingPage.classList.add("hidden");
    const resultsDiv = document.getElementById("results");
    if (resultsDiv) resultsDiv.classList.remove("hidden");
  });

  document.getElementById("backToMappingBtn").addEventListener("click", function () {
    document.getElementById("selectionPage").classList.add("hidden");
    mappingPage.classList.remove("hidden");
  });

  document.getElementById("continueBtn").addEventListener("click", function () {
    console.log(
      "Selected columns:",
      Array.from(document.getElementById("columnsToNormalize").selectedOptions).map(opt => opt.textContent)
    );
  });

  document.getElementById("oldFinalizeBtn")?.addEventListener("click", function () {
    const mapping = {};
    const activitySelect = document.getElementById("activitySelect");
    const timestampSelect = document.getElementById("timestampSelect");
    if (activitySelect.value) {
      mapping["activity"] = [activitySelect.value];
    }
    if (timestampSelect.value) {
      mapping["timestamp"] = [timestampSelect.value];
    }
    const container = document.getElementById("objectTypeAttributesContainer");
    Array.from(container.children).forEach(child => {
      const objectType = child.id.replace("objectType_", "");
      const select = child.querySelector("select");
      const attributes = Array.from(select.selectedOptions).map(opt => opt.value);
      mapping[objectType] = [objectType, ...attributes];
    });
    console.log("Final mapping:", mapping);
  });

  const dropZone = document.querySelector("label");
  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
  });
  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });
  function highlight(e) {
    e.preventDefault();
    dropZone.classList.add("file-drop-active");
  }
  function unhighlight(e) {
    e.preventDefault();
    dropZone.classList.remove("file-drop-active");
  }
  dropZone.addEventListener("drop", handleDrop, false);
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    fileInput.files = files;
    fileInput.dispatchEvent(new Event("change"));
  }
});
