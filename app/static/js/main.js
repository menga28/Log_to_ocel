document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("fileInput");
  const startMappingBtn = document.getElementById("startMappingBtn");
  const sampleBtn = document.getElementById("sampleBtn");
  const preview = document.getElementById("preview");
  const mappingPage = document.getElementById("mappingPage");

  fileInput.addEventListener("change", async function () {
    if (this.files.length) {
      const formData = new FormData();
      formData.append("file", this.files[0]);

      try {
        const response = await fetch("/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error("Upload failed");

        const data = await response.json();
        displayResults(data);
        startMappingBtn.disabled = false;
      } catch (error) {
        console.error("Error:", error);
        alert(error.message);
      }
    }
  });

  function setupMappingPage(data) {
    // Popola il selettore delle colonne annidate
    const columnsToNormalize = document.getElementById("columnsToNormalize");
    columnsToNormalize.innerHTML = "";
    data.nested_columns.forEach((col, index) => {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = col;
      columnsToNormalize.appendChild(option);
    });

    $('#columnsToNormalize').select2({
      placeholder: "Seleziona colonne da normalizzare",
      allowClear: true,
      width: '100%',
      selectionCssClass: 'border-gray-300',
      dropdownCssClass: 'border-gray-300',
      closeOnSelect: false // Permette selezione multipla senza chiudere il dropdown
    });

    // Popola la tabella di anteprima
    const table = document.querySelector("#mappingPage table");
    const thead = table.querySelector("thead tr");
    const tbody = table.querySelector("tbody");

    // Pulisci contenuto esistente
    thead.innerHTML = "";
    tbody.innerHTML = "";

    // Intestazioni colonne
    data.preview_columns.forEach(col => {
      const th = document.createElement("th");
      th.textContent = col;
      th.className = "px-4 py-2 bg-gray-100 sticky top-0";
      thead.appendChild(th);
    });

    // Righe dati (prime 10)
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

    // Gestione pulsanti
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
  
          if (!response.ok) throw new Error("Normalizzazione fallita");
  
          const result = await response.json();
          console.log(result.message);
  
          // Nasconde la schermata corrente
          document.getElementById("mappingPage").classList.add("hidden");
  
          // Mostra la nuova schermata di selezione
          setupSelectionPage(result.columns); 
  
      } catch (error) {
          console.error("Errore:", error);
          alert(error.message);
      }
  });
  
  function setupSelectionPage(columns) {
      const selectionPage = document.getElementById("selectionPage");
      selectionPage.classList.remove("hidden");
      
      const activitySelect = document.getElementById("activitySelect");
      const timestampSelect = document.getElementById("timestampSelect");
      const objectTypesSelect = document.getElementById("objectTypesSelect");
      const additionalEventAttributesSelect = document.getElementById("additionalEventAttributesSelect");
      const additionalObjectAttributesSelect = document.getElementById("additionalObjectAttributesSelect");
      const mainObjectColumnSelect = document.getElementById("mainObjectColumnSelect");
  
      // Svuota gli elementi esistenti
      [activitySelect, timestampSelect, objectTypesSelect, additionalEventAttributesSelect, additionalObjectAttributesSelect, mainObjectColumnSelect].forEach(select => {
          select.innerHTML = "";
      });
  
      // Popola i selettori
      columns.forEach(col => {
          const option = document.createElement("option");
          option.value = col;
          option.textContent = col;
  
          activitySelect.appendChild(option.cloneNode(true));
          timestampSelect.appendChild(option.cloneNode(true));
          objectTypesSelect.appendChild(option.cloneNode(true));
          additionalEventAttributesSelect.appendChild(option.cloneNode(true));
          additionalObjectAttributesSelect.appendChild(option.cloneNode(true));
          mainObjectColumnSelect.appendChild(option.cloneNode(true));
      });
  
      $('#objectTypesSelect').select2({ placeholder: "Seleziona oggetti", allowClear: true, width: '100%', closeOnSelect: false });
      $('#additionalEventAttributesSelect').select2({ placeholder: "Seleziona attributi evento", allowClear: true, width: '100%', closeOnSelect: false });
      $('#additionalObjectAttributesSelect').select2({ placeholder: "Seleziona attributi oggetto", allowClear: true, width: '100%', closeOnSelect: false });
  }

    // Aggiungi questa funzione
    function updateNormalizedPreview(data) {
      const table = document.querySelector("#mappingPage table");
      const thead = table.querySelector("thead tr");
      const tbody = table.querySelector("tbody");

      // Pulisci e aggiorna la tabella
      thead.innerHTML = "";
      tbody.innerHTML = "";

      // Intestazioni
      data.columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        th.className = "px-4 py-2 bg-gray-100 sticky top-0";
        thead.appendChild(th);
      });

      // Righe dati
      data.sample_data.forEach(row => {
        const tr = document.createElement("tr");
        data.columns.forEach(col => {
          const td = document.createElement("td");
          let content = row[col] || "";
          if (typeof content === "object") {
            content = JSON.stringify(content, null, 2);
          }
          td.textContent = content;
          td.className = "px-4 py-2 border whitespace-nowrap";
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }
  }

  function displayResults(data) {
    console.log("Displaying results:", data);
    const resultsDiv = document.createElement("div");
    resultsDiv.id = "results";
    resultsDiv.className = "mt-8";

    const { sample_data, ...filteredData } = data;
    const formatter = new JSONFormatter(filteredData, 2, {
      theme: "light",
      hoverPreviewEnabled: true,
      animateOpen: true,
      animateClose: true,
      open: 1 // Livello di espansione iniziale
    });

    // Costruisci la struttura correttamente
    const heading = document.createElement("h2");
    heading.className = "text-2xl font-semibold mb-4";
    heading.textContent = "Analysis Results";

    const container = document.createElement("div");
    container.className = "bg-gray-50 p-4 rounded overflow-x-auto";
    container.appendChild(formatter.render()); // Importante: appendChild diretto

    resultsDiv.appendChild(heading);
    resultsDiv.appendChild(container);

    // Rimuovi risultati esistenti
    const existingResults = document.getElementById("results");
    if (existingResults) existingResults.remove();

    // Aggiungi al DOM
    document.querySelector(".max-w-6xl").appendChild(resultsDiv);
  }

  startMappingBtn.addEventListener("click", async function () {
    try {
      const response = await fetch("/preview");
      if (!response.ok) throw new Error("Preview failed");

      const previewData = await response.json();
      setupMappingPage(previewData); // Chiamata alla nuova funzione
      mappingPage.classList.remove("hidden");

    } catch (error) {
      console.error("Error:", error);
      alert("Failed to load preview data");
    }
  });

  sampleBtn.addEventListener("click", async function () {
    try {
      const response = await fetch("/sample");
      if (!response.ok) throw new Error("Failed to load sample");

      const data = await response.json();
      displayPreview(data);
      startMappingBtn.disabled = false;
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while loading the sample file");
    }
  });

  function displayPreview(data) {
    const previewTable = preview.querySelector("table");
    const thead = previewTable.querySelector("thead tr");
    const tbody = previewTable.querySelector("tbody");

    // Clear existing content
    thead.innerHTML = "";
    tbody.innerHTML = "";

    // Add headers
    data.columns.forEach((column) => {
      const th = document.createElement("th");
      th.textContent = column;
      th.className = "px-4 py-2 text-left";
      thead.appendChild(th);
    });

    // Add data rows
    data.sample_data.forEach((row) => {
      const tr = document.createElement("tr");
      data.columns.forEach((column) => {
        const td = document.createElement("td");
        let content = row[column];
        if (typeof content === "object" && content !== null) {
          content = JSON.stringify(content);
        }
        td.textContent = content;
        td.className = "px-4 py-2 border";
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    // Update normalize columns select
    columnsToNormalize.innerHTML = "";
    data.nested_columns.forEach((column, index) => {
      const option = document.createElement("option");
      option.value = index;
      option.textContent = column;
      columnsToNormalize.appendChild(option);
    });

    preview.classList.remove("hidden");
  }

  document.getElementById("backBtn").addEventListener("click", function () {
    mappingPage.classList.add("hidden");
    const resultsDiv = document.getElementById("results");
    if (resultsDiv) resultsDiv.classList.remove("hidden");
  });

  document.getElementById("continueBtn").addEventListener("click", function () {
    // Logica per il prossimo step
    console.log("Selected columns:", Array.from(columnsToNormalize.selectedOptions).map(opt => opt.textContent));
  });

  // Drag and drop functionality
  const dropZone = document.querySelector("label");

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
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
