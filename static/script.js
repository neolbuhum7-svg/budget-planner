// Draws the "Spending by Category" doughnut chart.
(function () {
  const canvas = document.getElementById("spendChart");
  if (!canvas || typeof Chart === "undefined") return;

  const data = window.SPENDING || {};
  const labels = Object.keys(data);
  const values = Object.values(data);

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: [
          "#4f46e5", "#16a34a", "#f59e0b", "#dc2626", "#0ea5e9",
          "#a855f7", "#14b8a6", "#f97316", "#64748b", "#ec4899", "#84cc16",
        ],
      }],
    },
    options: {
      plugins: { legend: { position: "bottom" } },
    },
  });
})();
