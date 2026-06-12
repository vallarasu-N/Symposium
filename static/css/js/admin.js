document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const eventFilter = document.getElementById('eventFilter');
    const tableBody = document.getElementById('tableBody');
    const totalCount = document.getElementById('totalCount');
    const noResults = document.getElementById('noResults');

    function fetchRegistrations() {
        const search = searchInput.value.trim();
        const event = eventFilter.value;
        const url = `/admin/registrations?search=${encodeURIComponent(search)}&event=${encodeURIComponent(event)}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                tableBody.innerHTML = '';
                if (data.registrations.length === 0) {
                    noResults.style.display = 'block';
                } else {
                    noResults.style.display = 'none';
                    data.registrations.forEach(reg => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${reg.registration_id}</td>
                            <td>${reg.full_name}</td>
                            <td>${reg.college_name}</td>
                            <td>${reg.event_name}</td>
                            <td>${reg.email}</td>
                            <td>${reg.phone}</td>
                            <td>${reg.registration_date}</td>
                            <td><button class="delete-btn" data-id="${reg.id}"><i class="fas fa-trash"></i> Del</button></td>
                        `;
                        tableBody.appendChild(row);
                    });
                    attachDeleteEvents();
                }
                totalCount.textContent = data.total;
            })
            .catch(err => console.error('Error fetching data:', err));
    }

    function attachDeleteEvents() {
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                if (!confirm('Delete this registration?')) return;
                const id = this.getAttribute('data-id');
                fetch(`/admin/delete/${id}`, { method: 'DELETE' })
                    .then(() => fetchRegistrations());
            });
        });
    }

    searchInput.addEventListener('input', fetchRegistrations);
    eventFilter.addEventListener('change', fetchRegistrations);

    // Initial load
    fetchRegistrations();
});