// Function to create a card for a single insight
function createInsightCard(title, number) {
    return `
      <div class="col">
        <div class="card text-center insight-card">
          <div class="card-body">
            <div class="number counter" data-target="${number}">${number}</div>
            <div class="title">${title}</div>
          </div>
        </div>
      </div>
    `;
  }

  // Function to create a chart card
  function createChartCard(title, canvasId) {
    return `
      <div class="col-md-12">
        <div class="card chart-card">
          <div class="card-body">
            <h5 class="card-title">${title}</h5>
            <canvas id="${canvasId}"></canvas>
          </div>
        </div>
      </div>
    `;
  }

  // Function to render a bar chart
  function renderBarChart(canvasId, labels, data, label, backgroundColor = 'rgba(213,90,144, 0.2)', borderColor = 'rgba(213,90,144, 1)') {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          backgroundColor: backgroundColor,
          borderColor: borderColor,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
  const dashboard = document.getElementById("dashboard");
  // Function to create the dashboard
  function createDashboard(insights) {
    // Clear any existing content
    dashboard.innerHTML = "";

    // News Insights
    dashboard.innerHTML += `<h5 class="card-title">News Insights</h5>`;
    dashboard.innerHTML += createInsightCard("Total News Articles", insights.news_insights.total_news_articles);
    dashboard.innerHTML += createInsightCard("Avg Title Length",insights.news_insights.avg_title_length.toFixed(2));
    dashboard.innerHTML += createInsightCard("Max Title Length", insights.news_insights.max_title_length);
    dashboard.innerHTML += createInsightCard("Avg Abstract Length",insights.news_insights.avg_abstract_length.toFixed(2));
    dashboard.innerHTML += createInsightCard("Max Abstract Length", insights.news_insights.max_abstract_length);
    // Behaviors Insights
    dashboard.innerHTML += `<h5 class="card-title">Behaviors Insights</h5>`;
    dashboard.innerHTML += createInsightCard("Total Users", insights.behaviors_insights.total_users);
    dashboard.innerHTML += createInsightCard("Total Impressions", insights.behaviors_insights.total_impressions);
    dashboard.innerHTML += createInsightCard(
      "Click Through Rate (CTR)",
      `${(insights.behaviors_insights.click_through_rate * 100).toFixed(2)}`
    );
    dashboard.innerHTML += createInsightCard(
      "Avg Click History Length",
      insights.behaviors_insights.avg_click_history_length.toFixed(2)
    );
    dashboard.innerHTML += createInsightCard(
      "Max Click History Length",
      insights.behaviors_insights.max_click_history_length
    );

    

    // Category Distribution Chart
    //dashboard.innerHTML += createChartCard("Category Distribution", "categoryDistributionChart");
    const categoryLabels = Object.keys(insights.news_insights.category_distribution);
    const categoryData = Object.values(insights.news_insights.category_distribution);
    console.log(categoryLabels);
    console.log(categoryData);

    //renderBarChart("categoryDistributionChart", categoryLabels, categoryData, "Articles by Category",'rgba(255, 99, 132, 0.2)', 'rgba(255, 99, 132, 1)');

    // CTR by Category Chart
    dashboard.innerHTML += createChartCard("Click Through Rate (CTR) by Category", "ctrByCategoryChart");
    const ctrLabels = Object.keys(insights.combined_insights.ctr_by_category);
    const ctrData = Object.values(insights.combined_insights.ctr_by_category).map(ctr => (ctr * 100).toFixed(2));
    renderBarChart("ctrByCategoryChart", ctrLabels, ctrData, "CTR (%) by Category");
    animateCounters();
  }

  // Fetch insights and populate the dashboard
  async function fetchInsights() {
    try {
        dashboard.innerHTML = `
        <div class="d-flex justify-content-center">
<div class="spinner-border text-warning text-center" role="status" style="width: 5rem; height: 5rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
</div>
        `
      const response = await fetch("/get_insights"); // Replace with your API URL
      if (!response.ok) {
        throw new Error("Failed to fetch insights.");
      }
      const insights = await response.json();
      createDashboard(insights);
    } catch (error) {
      console.error("Error fetching insights:", error);
    }
  }

  // Initialize the dashboard on page load
  document.addEventListener("DOMContentLoaded", fetchInsights);

  // Counter Animation Function
  function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
      const target = +counter.getAttribute('data-target');
      const increment = target / 100; // Adjust this for speed
      let current = 0;

      const updateCounter = () => {
        current += increment;
        if (current < target) {
          counter.textContent = Math.ceil(current);
          requestAnimationFrame(updateCounter); // Smooth animation
        } else {
          
          counter.textContent = new Intl.NumberFormat().format(target);; // Ensure the final value is correct
        }
      };

      updateCounter();
    });
  }