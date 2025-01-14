document.addEventListener('DOMContentLoaded', () => {
    loadStudentList();
});

function loadStudentList() {
    fetch('student_list.txt')
        .then(response => response.text())
        .then(data => {
            const students = data.split('\n').map(name => name.trim()).filter(name => name);
            const nameSelect = document.getElementById('name');
            students.forEach(student => {
                const option = document.createElement('option');
                option.value = student;
                option.textContent = student;
                nameSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading student list:', error));
}

function addDuty() {
    const category = document.getElementById('category').value;
    const group = document.getElementById('group').value;
    const name = document.getElementById('name').value;

    if (category && group && name) {
        const tbody = document.getElementById('dutyList');
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${category}</td>
            <td>${group}</td>
            <td>${name}</td>
            <td>
                <button class="btn btn-delete" onclick="deleteDuty(this)">删除</button>
            </td>`;
        tbody.appendChild(row);
    } else {
        alert('请填写所有字段');
    }
}

function deleteDuty(button) {
    const row = button.parentNode.parentNode;
    row.remove();
}

function exportData() {
    const rows = document.querySelectorAll('#dutyList tr');
    const data = Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td');
        return {
            category: cells[0].textContent,
            group: cells[1].textContent,
            name: cells[2].textContent
        };
    });
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'duty_list.json';
    a.click();
    URL.revokeObjectURL(url);
}

function importData() {
    document.getElementById('importFile').click();
}

function handleFileImport(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const data = JSON.parse(e.target.result);
            const tbody = document.getElementById('dutyList');
            tbody.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.category}</td>
                    <td>${item.group}</td>
                    <td>${item.name}</td>
                    <td>
                        <button class="btn btn-delete" onclick="deleteDuty(this)">删除</button>
                    </td>`;
                tbody.appendChild(row);
            });
        };
        reader.readAsText(file);
    }
}