async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Dashboard request failed");
        }

        const data = await response.json();

        document.getElementById("totalFeedback").textContent = data.total;
        document.getElementById("positiveFeedback").textContent = data.positive;
        document.getElementById("negativeFeedback").textContent = data.negative;
        document.getElementById("neutralFeedback").textContent = data.neutral;

        renderSentimentChart(data);
        renderCategoryChart(data.categories);
        renderThemes(data.themes);
        renderRecent(data.recent);
    } catch (error) {
        console.error(error);
    }
}

function renderSentimentChart(data) {
    const canvas = document.getElementById("sentimentChart");

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: ["Positive", "Negative", "Neutral"],
            datasets: [{
                data: [data.positive, data.negative, data.neutral]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}

function renderCategoryChart(categories) {
    const canvas = document.getElementById("categoryChart");

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: categories.map(item => item.name),
            datasets: [{
                label: "Feedback",
                data: categories.map(item => item.count)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function renderThemes(themes) {
    const container = document.getElementById("themesList");

    if (!themes.length) {
        container.innerHTML = '<div class="empty">No themes yet.</div>';
        return;
    }

    container.innerHTML = themes.map(theme => `
        <div class="theme-row">
            <strong>${escapeHtml(theme.name)}</strong>
            <span class="theme-count">${theme.count}</span>
        </div>
    `).join("");
}

function renderRecent(items) {
    const container = document.getElementById("recentFeedback");

    if (!items.length) {
        container.innerHTML = '<div class="empty">No feedback yet.</div>';
        return;
    }

    container.innerHTML = items.map(item => `
        <div class="recent-item">
            <div class="recent-top">
                <strong>${escapeHtml(item.customer_name || "Anonymous")}</strong>
                <span class="badge ${item.sentiment.toLowerCase()}">${escapeHtml(item.sentiment)}</span>
            </div>
            <div class="recent-message">
                ${escapeHtml(item.message.length > 110 ? item.message.slice(0, 110) + "..." : item.message)}
            </div>
        </div>
    `).join("");
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

loadDashboard();
