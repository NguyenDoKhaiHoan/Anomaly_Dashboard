function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

let activeTooltip = null;

function showTooltip(event, canvas, rows, pointIndex) {
  hideTooltip();
  
  const row = rows[pointIndex];
  if (!row) return;
  
  const payload = row.raw_payload ?? row.raw_event ?? {};
  
  const tooltip = document.createElement("div");
  tooltip.className = "chart-tooltip";
  
  // Build field list based on available data
  const score = Number(row.anomaly_score ?? 0).toFixed(4);
  const time = row.time || "";
  const latency = row.detector_latency_ms ? `<div class="tooltip-row"><span>Latency:</span> ${row.detector_latency_ms.toFixed(2)}ms</div>` : "";
  
  // Get first 5 fields from payload for display
  const payloadKeys = Object.keys(payload).slice(0, 5);
  const payloadFields = payloadKeys.map(key => {
    const val = payload[key];
    const displayVal = typeof val === 'number' ? val.toFixed(2) : val;
    return `<div class="tooltip-row"><span>${key}:</span> <strong>${displayVal}</strong></div>`;
  }).join('');
  
  tooltip.innerHTML = `
    <div class="tooltip-time">${time}</div>
    ${payloadFields}
    <div class="tooltip-row"><span>Score:</span> <strong>${score}</strong></div>
    ${latency}
    <div class="tooltip-raw">${JSON.stringify(payload, null, 2)}</div>
  `;
  
  document.body.appendChild(tooltip);
  activeTooltip = tooltip;
  
  const x = event.clientX;
  const y = event.clientY;
  
  tooltip.style.left = (x + 12) + "px";
  tooltip.style.top = (y - 10) + "px";
  
  requestAnimationFrame(() => {
    if (tooltip.getBoundingClientRect().right > window.innerWidth) {
      tooltip.style.left = (x - tooltip.offsetWidth - 12) + "px";
    }
    if (tooltip.getBoundingClientRect().bottom > window.innerHeight) {
      tooltip.style.top = (y - tooltip.offsetHeight) + "px";
    }
  });
}

function hideTooltip() {
  if (activeTooltip) {
    activeTooltip.remove();
    activeTooltip = null;
  }
}

export function drawLineChart(canvas, rows, dataKey) {
  if (!canvas) return;
  hideTooltip();
  
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  const values = rows.map((item) => toNumber(item[dataKey]));
  if (values.length < 2) {
    ctx.fillStyle = "rgba(168, 181, 217, 0.8)";
    ctx.font = "14px Segoe UI";
    ctx.fillText("Not enough data", 16, 24);
    return;
  }

  // Calculate range dynamically based on actual data
  const min = Math.min(0, Math.min(...values));
  const max = Math.max(...values) * 1.1;
  const span = max - min || 1;
  const margin = { top: 20, right: 50, bottom: 30, left: 50 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Grid lines
  ctx.strokeStyle = "rgba(99, 102, 241, 0.15)";
  ctx.lineWidth = 1;
  ctx.font = "11px Segoe UI";
  ctx.fillStyle = "rgba(168, 181, 217, 0.7)";
  ctx.textAlign = "right";
  
  const gridLines = 5;
  for (let i = 0; i <= gridLines; i += 1) {
    const y = margin.top + (innerHeight / gridLines) * i;
    const value = max - (span / gridLines) * i;
    
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(width - margin.right, y);
    ctx.stroke();
    
    ctx.fillText(value.toFixed(2), margin.left - 8, y + 4);
  }

  // Calculate points
  const points = values.map((value, index) => {
    const x = margin.left + (innerWidth * index) / Math.max(values.length - 1, 1);
    const y = height - margin.bottom - ((value - min) / span) * innerHeight;
    return { x, y, isAnomaly: Boolean(rows[index]?.is_anomaly), value, index };
  });

  // Draw the line
  ctx.strokeStyle = "#6366f1";
  ctx.lineWidth = 2;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  points.forEach((point, index) => {
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.stroke();

  // Draw points - red for anomaly, cyan for normal
  points.forEach((point) => {
    const radius = point.isAnomaly ? 5 : 3.5;
    
    ctx.beginPath();
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = point.isAnomaly ? "#ef4444" : "#22d3ee";
    ctx.fill();
    ctx.strokeStyle = "rgba(10, 14, 39, 0.9)";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });

  // X-axis labels
  ctx.fillStyle = "rgba(168, 181, 217, 0.7)";
  ctx.font = "10px Segoe UI";
  ctx.textAlign = "center";
  
  const labelCount = Math.min(6, points.length);
  const labelStep = Math.max(1, Math.floor(points.length / labelCount));
  for (let i = 0; i < points.length; i += labelStep) {
    const x = points[i].x;
    ctx.fillText(rows[i]?.time?.slice(-5) || "", x, height - margin.bottom + 20);
  }

  // Store points for hover
  canvas._chartPoints = points;
  canvas._chartRows = rows;
  
  canvas.removeEventListener("mousemove", handleMouseMove);
  canvas.removeEventListener("mouseleave", handleMouseLeave);
  canvas.style.cursor = "crosshair";
  
  function handleMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mouseX = (e.clientX - rect.left) * scaleX;
    const mouseY = (e.clientY - rect.top) * scaleY;
    
    const hitRadius = 15;
    let foundIndex = -1;
    
    for (let i = 0; i < points.length; i++) {
      const dx = points[i].x - mouseX;
      const dy = points[i].y - mouseY;
      if (Math.sqrt(dx * dx + dy * dy) < hitRadius) {
        foundIndex = i;
        break;
      }
    }
    
    if (foundIndex >= 0) {
      canvas.style.cursor = "pointer";
      showTooltip(e, canvas, rows, foundIndex);
    } else {
      canvas.style.cursor = "crosshair";
      hideTooltip();
    }
  }
  
  function handleMouseLeave() {
    hideTooltip();
  }
  
  canvas.addEventListener("mousemove", handleMouseMove);
  canvas.addEventListener("mouseleave", handleMouseLeave);
}
