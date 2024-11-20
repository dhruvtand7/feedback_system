/*static/js/scripts.js */

function startReviewCycle() {
    const endDate = prompt("Enter end date for review cycle (YYYY-MM-DD):");
    if (!endDate) return;

    fetch('/dean/start_review_cycle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ end_date: endDate })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Review cycle started successfully');
            location.reload();
        } else {
            alert('Failed to start review cycle: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to start review cycle');
    });
}

function closeReviewCycle() {
    if (!confirm('Are you sure you want to close the current review cycle?')) return;

    fetch('/dean/close_review_cycle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Review cycle closed successfully');
            location.reload();
        } else {
            alert('Failed to close review cycle: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to close review cycle');
    });
}

function submitFeedback(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Feedback submitted successfully');
            location.reload();
        } else {
            alert('Failed to submit feedback: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to submit feedback');
    });
}