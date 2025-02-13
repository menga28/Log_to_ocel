document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const startMappingBtn = document.getElementById('startMappingBtn');
    const sampleBtn = document.getElementById('sampleBtn');
    const preview = document.getElementById('preview');
    const mappingPage = document.getElementById('mappingPage');

    fileInput.addEventListener('change', async function() {
        if (this.files.length) {
            const formData = new FormData();
            formData.append('file', this.files[0]);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error('Upload failed');
                
                const data = await response.json();
                displayResults(data);
                startMappingBtn.disabled = false;
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while processing the file');
            }
        }
    });

    function displayResults(data) {
        const resultsDiv = document.createElement('div');
        resultsDiv.id = 'results';
        resultsDiv.className = 'mt-8';

        let html = `
            <h2 class="text-2xl font-semibold mb-4">Analysis Results</h2>
            <pre class="bg-gray-50 p-4 rounded overflow-x-auto">
${JSON.stringify(data, null, 2)}
            </pre>
        `;

        resultsDiv.innerHTML = html;

        // Rimuove i risultati precedenti se esistono
        const existingResults = document.getElementById('results');
        if (existingResults) {
            existingResults.remove();
        }

        // Aggiunge i nuovi risultati
        document.querySelector('.max-w-6xl').appendChild(resultsDiv);
    }

    startMappingBtn.addEventListener('click', function() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) resultsDiv.classList.add('hidden');
        mappingPage.classList.remove('hidden');
    });

    sampleBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/sample');
            if (!response.ok) throw new Error('Failed to load sample');

            const data = await response.json();
            displayPreview(data);
            startMappingBtn.disabled = false;
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while loading the sample file');
        }
    });

    function displayPreview(data) {
        const previewTable = preview.querySelector('table');
        const thead = previewTable.querySelector('thead tr');
        const tbody = previewTable.querySelector('tbody');

        // Clear existing content
        thead.innerHTML = '';
        tbody.innerHTML = '';

        // Add headers
        data.columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            th.className = 'px-4 py-2 text-left';
            thead.appendChild(th);
        });

        // Add data rows
        data.sample_data.forEach(row => {
            const tr = document.createElement('tr');
            data.columns.forEach(column => {
                const td = document.createElement('td');
                let content = row[column];
                if (typeof content === 'object' && content !== null) {
                    content = JSON.stringify(content);
                }
                td.textContent = content;
                td.className = 'px-4 py-2 border';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        // Update normalize columns select
        columnsToNormalize.innerHTML = '';
        data.nested_columns.forEach((column, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = column;
            columnsToNormalize.appendChild(option);
        });

        preview.classList.remove('hidden');
    }

    // Drag and drop functionality
    const dropZone = document.querySelector('label');

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        e.preventDefault();
        dropZone.classList.add('file-drop-active');
    }

    function unhighlight(e) {
        e.preventDefault();
        dropZone.classList.remove('file-drop-active');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        fileInput.files = files;
        fileInput.dispatchEvent(new Event('change'));
    }
});
