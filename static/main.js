// This file contains the JavaScript code for the online company website. 
// It includes functionality for interactive elements such as navigation menus and image sliders.

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Image slider functionality
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.style.display = (i === index) ? 'block' : 'none';
        });
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        showSlide(currentSlide);
    }

    if (slides.length > 0) {
        const nextBtn = document.querySelector('.next');
        const prevBtn = document.querySelector('.prev');
        if (nextBtn) nextBtn.addEventListener('click', nextSlide);
        if (prevBtn) prevBtn.addEventListener('click', prevSlide);
        showSlide(currentSlide);
    }

    // Contact form submission
    document.querySelector('.contact-section form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const name = document.getElementById('name').value.trim()
        const email = document.getElementById('email').value.trim();
        const message = document.getElementById('message').value.trim();

        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, message })
        });

        const result = await response.json();
        if (response.ok) {
            this.style.display = 'none';
            document.getElementById('contact-success').style.display = 'block';
            document.getElementById('contact-success').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert(result.error || 'Something went wrong. Please try again.');
        }
    });

    let allMessages = [];

    function renderMessages(messages) {
      const tbody = document.querySelector('#messages-table tbody');
      tbody.innerHTML = '';
      messages.forEach(msg => {
        tbody.innerHTML += `<tr data-id="${msg.id}">
          <td>${msg.id}</td>
          <td>${msg.name}</td>
          <td>${msg.email}</td>
          <td>${msg.message}</td>
          <td>
            <button class="btn btn-danger btn-sm delete-btn">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>`;
      });

      // Add event listeners for delete buttons
      document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function() {
          const row = this.closest('tr');
          const id = row.getAttribute('data-id');
          if (confirm('Are you sure you want to delete this message?')) {
            fetch(`/admin/messages/${id}`, { method: 'DELETE' })
              .then(res => res.json())
              .then(result => {
                if (result.success) row.remove();
                else alert('Failed to delete message.');
              });
          }
        });
      });
    }

    // Fetch messages and enable search/export
    fetch('/admin/messages')
      .then(res => res.json())
      .then(data => {
        allMessages = data;
        renderMessages(allMessages);
      });

    document.getElementById('search-input').addEventListener('input', function() {
      const q = this.value.toLowerCase();
      renderMessages(allMessages.filter(
        m => m.name.toLowerCase().includes(q) ||
             m.email.toLowerCase().includes(q) ||
             m.message.toLowerCase().includes(q)
      ));
    });

    document.getElementById('export-btn').addEventListener('click', function() {
      let csv = "ID,Name,Email,Message\n";
      allMessages.forEach(m => {
        csv += `"${m.id}","${m.name.replace(/"/g,'""')}","${m.email.replace(/"/g,'""')}","${m.message.replace(/"/g,'""')}"\n`;
      });
      const blob = new Blob([csv], {type: 'text/csv'});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'messages.csv';
      a.click();
      URL.revokeObjectURL(url);
    });
});