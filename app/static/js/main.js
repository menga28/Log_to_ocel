document.addEventListener("DOMContentLoaded", function () {
  // Declare as "let" so we can update them dynamically after OCEL creation.
  let availableTypes = ["txHash", "inputs_inputName", "sender", "contractAddress", "gasUsed", "activity"];
  let availableActivities = ["approve", "sendFrom", "transfer"];

  const fileInput = document.getElementById("fileInput");
  const startMappingBtn = document.getElementById("startMappingBtn");
  const sampleBtn = document.getElementById("sampleBtn");
  const preview = document.getElementById("preview");
  const mappingPage = document.getElementById("mappingPage");

  // --- Home Screen: File Upload / Sample ---
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

  // Helper: Derive a JSON schema (skeleton) from an object.
  function getSchemaFromObject(obj) {
    const schema = {};
    Object.keys(obj).forEach(key => {
      const val = obj[key];
      if (Array.isArray(val)) {
        schema[key] = val.length > 0 ? [getSchemaFromObject(val[0])] : [];
      } else if (typeof val === "object" && val !== null) {
        schema[key] = getSchemaFromObject(val);
      } else {
        schema[key] = ""; // omit actual value
      }
    });
    return schema;
  }

  // Display preview data on the home screen.
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
    // Update "Columns to Normalize" select.
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

  // --- Mapping Page ---
  function setupMappingPage(data) {
    const columnsToNormalize = document.getElementById("columnsToNormalize");
    columnsToNormalize.innerHTML = "";
    data.nested_columns.forEach((col, index) => {
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
    data.preview_columns.forEach(col => {
      const th = document.createElement("th");
      th.textContent = col;
      th.className = "px-4 py-2 bg-gray-100 sticky top-0";
      thead.appendChild(th);
    });
    data.sample_data.slice(0, 10).forEach(row => {
      const tr = document.createElement("tr");
      data.preview_columns.forEach(col => {
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
    // /normalize call: Send selected nested columns indexes.
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

    // Populate the Select Attributes page.
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
      // Finalize button in the Select Attributes page calls /set_ocel_parameters.
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
          // Update dynamic qualifier values with the ones received from backend.
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

  // Update dynamic object attributes container based on selected object types.
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

  // --- QUALIFIER PAGE FUNCTIONS ---
  function initializeQualifierRows() {
    const container = document.getElementById("qualifierContainer");
    container.innerHTML = "";
    addQualifierRow();
  }

  function addQualifierRow() {
    const container = document.getElementById("qualifierContainer");
    const rowDiv = document.createElement("div");
    rowDiv.className = "qualifier-row mb-2 flex space-x-2";
    const typeSelect = document.createElement("select");
    typeSelect.className = "ocel-type-select p-2 border rounded";
    availableTypes.forEach(type => {
      const option = document.createElement("option");
      option.value = type;
      option.textContent = type;
      typeSelect.appendChild(option);
    });
    const activitySelect = document.createElement("select");
    activitySelect.className = "ocel-activity-select p-2 border rounded";
    availableActivities.forEach(act => {
      const option = document.createElement("option");
      option.value = act;
      option.textContent = act;
      activitySelect.appendChild(option);
    });
    const qualifierInput = document.createElement("input");
    qualifierInput.type = "text";
    qualifierInput.placeholder = "Enter qualifier";
    qualifierInput.className = "qualifier-input p-2 border rounded flex-grow";
    rowDiv.appendChild(typeSelect);
    rowDiv.appendChild(activitySelect);
    rowDiv.appendChild(qualifierInput);
    container.appendChild(rowDiv);
    rowDiv.addEventListener("change", function () {
      const rows = container.getElementsByClassName("qualifier-row");
      if (rows[rows.length - 1] === rowDiv && qualifierInput.value.trim() !== "") {
        addQualifierRow();
      }
    });
  }

  // When "Set Relationship Qualifier" is clicked, build the qualifier map and send it to the backend.
  document.getElementById("submitQualificationsBtn").addEventListener("click", async function () {
    const container = document.getElementById("qualifierContainer");
    const rows = container.getElementsByClassName("qualifier-row");
    const qualifierMap = {};
    Array.from(rows).forEach(row => {
      const type = row.querySelector(".ocel-type-select").value;
      const activity = row.querySelector(".ocel-activity-select").value;
      const qualifier = row.querySelector(".qualifier-input").value.trim();
      if (qualifier !== "") {
        // Build key as "type|activity"
        qualifierMap[`${type}|${activity}`] = qualifier;
      }
    });
    try {
      const response = await fetch("/set_relationship_qualifiers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qualifier_map: qualifierMap })
      });
      if (!response.ok) throw new Error("Setting relationship qualifiers failed");
      const result = await response.json();
      console.log(result.message);
    } catch (error) {
      console.error("Error:", error);
      alert(error.message);
    }
  });

  // Back button from qualifier page.
  document.getElementById("backFromQualifierBtn").addEventListener("click", function () {
    document.getElementById("qualifierPage").classList.add("hidden");
    document.getElementById("selectionPage").classList.remove("hidden");
  });

  // "Start OCEL Mapping" button on the home screen.
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

  // OLD FINALIZE (for debugging)
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
