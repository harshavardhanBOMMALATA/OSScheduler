/* =====================================================
   GLOBAL CHART REFERENCES
===================================================== */
let ganttChart = null;
let timelineChart = null;

/* =====================================================
   DOM REFERENCES (DECLARE ONCE)
===================================================== */
const algorithmSelect = document.getElementById("algorithmSelect");
const tableBody = document.getElementById("processTableBody");

/* =====================================================
   PRIORITY COLUMN TOGGLE
===================================================== */
function togglePriorityColumn() {
  const show =
    algorithmSelect.value === "Priority" ||
    algorithmSelect.value === "Preemptive Priority";

  document.querySelectorAll(".priority-col").forEach(col => {
    col.style.display = show ? "table-cell" : "none";
  });
}

algorithmSelect.addEventListener("change", togglePriorityColumn);
togglePriorityColumn();

/* =====================================================
   ADD / REMOVE PROCESS
===================================================== */
document.getElementById("addProcessBtn").onclick = () => {
  const rowCount = tableBody.rows.length + 1;

  const row = document.createElement("tr");
  row.innerHTML = `
    <td class="pid">P${rowCount}</td>
    <td><input type="number" value="0"></td>
    <td><input type="text"></td>
    <td class="priority-col"><input type="number"></td>
  `;

  tableBody.appendChild(row);
  togglePriorityColumn();
};

document.getElementById("removeProcessBtn").onclick = () => {
  if (tableBody.rows.length > 1) {
    tableBody.deleteRow(-1);
  }
};

/* =====================================================
   API MAP (YOUR URLs)
===================================================== */
const apiMap = {
  FCFS: "/api/fcfs/",
  SJF: "/api/sjf/",
  SRTF: "/api/srtf/",
  LJF: "/api/ljf/",
  LRTF: "/api/lrtf/",
  Priority: "/api/priority/",
  "Preemptive_Priority": "/api/priority/"
};

/* =====================================================
   RUN SCHEDULER
===================================================== */
document.getElementById("runSchedulerBtn").onclick = () => {

  const algorithm = algorithmSelect.value;
  const processes = [];

  document.querySelectorAll("#processTableBody tr").forEach(row => {

    const pid = row.children[0].innerText;
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2]
      .querySelector("input")
      .value
      .split(",")
      .map(v => parseInt(v.trim()))
      .filter(v => !isNaN(v));

    const process = { pid, arrival, bursts };

    if (
      algorithm === "Priority" ||
      algorithm === "Preemptive Priority"
    ) {
      process.priority = parseInt(
        row.children[3].querySelector("input").value
      );
    }

    processes.push(process);
  });

  fetch(apiMap[algorithm], {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.getElementById("csrfToken").value
    },
    body: JSON.stringify({
      context_switch: parseInt(
        document.getElementById("contextSwitchInput").value
      ) || 0,
      processes
    })
  })
  .then(res => res.json())
  .then(data => {

    /* ===== VISUALIZATION DATA (CRITICAL FIX) ===== */
    timelineData = data.timeline;
    currentTime = 0;
    /* ============================================ */

    /* ================= METRICS TABLE ================= */
    const metricsTbody =
      document.querySelector(".col.card table tbody");

    metricsTbody.innerHTML = "";

    data.processes.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="pid">${p.pid}</td>
        <td>${p.arrival}</td>
        <td>${p.burst_time}</td>
        <td>${p.completion_time}</td>
        <td>${p.tat}</td>
        <td>${p.wt}</td>
        <td>${p.rt}</td>
      `;
      metricsTbody.appendChild(tr);
    });

    /* ================= METRICS BOXES ================= */
    const metricBoxes = document.querySelectorAll(".metrics-box");

    metricBoxes[0].innerText = `Avg TAT: ${data.average.tat.toFixed(2)}`;
    metricBoxes[1].innerText = `Avg WT: ${data.average.wt.toFixed(2)}`;
    metricBoxes[2].innerText = `Avg RT: ${data.average.rt.toFixed(2)}`;

    const totalCpu = data.processes.reduce(
      (s, p) => s + p.burst_time, 0
    );

    metricBoxes[3].innerText =
      `CPU Utilization: ${((totalCpu / data.system.total_time) * 100).toFixed(2)}%`;
    metricBoxes[4].innerText =
      `Throughput: ${data.system.throughput.toFixed(2)}`;
    metricBoxes[5].innerText =
      `Total Time: ${data.system.total_time}`;

    /* ================= GANTT CHART ================= */
    if (ganttChart) ganttChart.destroy();

    ganttChart = new ApexCharts(
      document.querySelector("#gantt"),
      {
        chart: {
          type: "rangeBar",
          height: 220,
          toolbar: { show: false },
          zoom: { enabled: false }
        },
        plotOptions: {
          bar: { horizontal: true }
        },
        tooltip: {
          custom: ({ w, seriesIndex, dataPointIndex }) => {
            const d =
              w.config.series[seriesIndex].data[dataPointIndex];
            return `
              <div style="padding:8px">
                <b>PID:</b> ${d.pid}<br>
                <b>Start:</b> ${d.y[0]}<br>
                <b>End:</b> ${d.y[1]}
              </div>
            `;
          }
        },
        series: [{
          data: data.gantt.map(g => ({
            x: "CPU",
            y: [g.start, g.end],
            pid: g.pid
          }))
        }]
      }
    );

    ganttChart.render();

    /* ================= TIMELINE CHART ================= */
    if (timelineChart) timelineChart.destroy();

    const timelineMap = {};
    data.gantt.forEach(g => {
      if (!timelineMap[g.pid]) timelineMap[g.pid] = [];
      timelineMap[g.pid].push({
        x: g.pid,
        y: [g.start, g.end]
      });
    });

    timelineChart = new ApexCharts(
      document.querySelector("#timeline"),
      {
        chart: {
          type: "rangeBar",
          height: 320,
          toolbar: { show: false },
          zoom: { enabled: false }
        },
        plotOptions: {
          bar: {
            horizontal: true,
            barHeight: "60%"
          }
        },
        series: Object.keys(timelineMap).map(pid => ({
          name: pid,
          data: timelineMap[pid]
        }))
      }
    );

    timelineChart.render();
  })
  .catch(err => console.error("Scheduler Error:", err));
};




function visualization() {
  const algorithm = document.getElementById("algorithmSelect").value;

  if (algorithm === "FCFS") {
    fcfs_visualization();
  } else if (algorithm === "SJF") {
    sjf_visualization();  
  } else if (algorithm === "SRTF") {
    srtf_visualization(); 
  } else if (algorithm === "LJF") {
    ljf_visualization();   
  } else if (algorithm === "LRTF") {
    lrtf_visualization();  
  } else if (algorithm === "Priority") {
    priority_visualization(); 
  } else if (algorithm === "Preemptive Priority") {
    preemptive_priority_visualization(); 
  } else {
    alert("Unknown algorithm selected");
  }
}



async function fcfs_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = []; // { process, remainingIO }
  let current = null;

  /* LOAD ALL INTO NEW */
  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2]
      .querySelector("input")
      .value.split(",")
      .map(v => parseInt(v.trim()))
      .filter(v => !isNaN(v));

    const p = {
      pid,
      arrival,
      bursts,
      index: 0,
      card: createProcessCard(pid)
    };

    newQ.push(p);
    newBox.appendChild(p.card);
  });

  newQ.sort((a, b) => a.arrival - b.arrival);

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    /* 1️⃣ RUNNING EXECUTES */
    if (current) {
      current.bursts[current.index]--;

      if (current.bursts[current.index] === 0) {
        current.index++;

        // RUNNING → BLOCKED
        if (current.index < current.bursts.length) {
          blockedQ.push({
            process: current,
            remainingIO: current.bursts[current.index]
          });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        }
        // RUNNING → TERMINATED
        else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }

        current = null;
      }
    }

    /* 2️⃣ BLOCKED → READY */
    let movedBlocked = false;
    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;

      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
        movedBlocked = true;
      } else i++;
    }

    if (movedBlocked) await sleep(150);

    /* 3️⃣ NEW → READY */
    let movedNew = false;
    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
        movedNew = true;
      } else i++;
    }

    if (movedNew) await sleep(150);

    /* 4️⃣ READY → RUNNING */
    if (!current && readyQ.length) {
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    /* 5️⃣ ADVANCE TIME */
    time++;
    timerEl.innerText = time;
  }
}



function sleep(ms) {
  return new Promise(res => setTimeout(res, ms));
}

function createProcessCard(pid) {
  const d = document.createElement("div");
  d.className = "process-card";
  d.innerText = pid;
  return d;
}

function clearAllStateBoxes() {
  ["newBox","readyBox","runningBox","blockedBox","terminatedBox"]
    .forEach(id => {
      const box = document.getElementById(id);
      if (box) box.innerHTML = "";
    });
}




function blinkArrow(className) {
  const arrow = document.querySelector(className);
  if (!arrow) return;

  arrow.style.color = "blue";

  setTimeout(() => {
    arrow.style.color = "";
  }, 1000);
}


function createProcessCard(pid) {
  const div = document.createElement("div");
  div.className = "process-card";
  div.innerText = pid;
  return div;
}

function clearAllStateBoxes() {
  ["newBox", "readyBox", "runningBox", "blockedBox", "terminatedBox"]
    .forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = "";
    });
}



async function sjf_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = []; // { process, remainingIO }
  let current = null;

  /* LOAD ALL INTO NEW */
  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2]
      .querySelector("input")
      .value.split(",")
      .map(v => parseInt(v.trim()))
      .filter(v => !isNaN(v));

    const p = {
      pid,
      arrival,
      bursts,
      index: 0,
      card: createProcessCard(pid)
    };

    newQ.push(p);
    newBox.appendChild(p.card);
  });

  newQ.sort((a, b) => a.arrival - b.arrival);

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    /* RUNNING */
    if (current) {
      current.bursts[current.index]--;

      if (current.bursts[current.index] === 0) {
        current.index++;

        if (current.index < current.bursts.length) {
          blockedQ.push({
            process: current,
            remainingIO: current.bursts[current.index]
          });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        } else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }

        current = null;
      }
    }

    /* BLOCKED → READY */
    let movedBlocked = false;
    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;
      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
        movedBlocked = true;
      } else i++;
    }
    if (movedBlocked) await sleep(150);

    /* NEW → READY */
    let movedNew = false;
    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
        movedNew = true;
      } else i++;
    }
    if (movedNew) await sleep(150);

    /* READY → RUNNING (SJF PICK) */
    if (!current && readyQ.length) {
      readyQ.sort(
        (a, b) => a.bursts[a.index] - b.bursts[b.index]
      );
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}




async function ljf_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = []; // { process, remainingIO }
  let current = null;

  /* LOAD ALL INTO NEW */
  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2]
      .querySelector("input")
      .value.split(",")
      .map(v => parseInt(v.trim()))
      .filter(v => !isNaN(v));

    const p = {
      pid,
      arrival,
      bursts,
      index: 0,
      card: createProcessCard(pid)
    };

    newQ.push(p);
    newBox.appendChild(p.card);
  });

  newQ.sort((a, b) => a.arrival - b.arrival);

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    /* RUNNING */
    if (current) {
      current.bursts[current.index]--;

      if (current.bursts[current.index] === 0) {
        current.index++;

        if (current.index < current.bursts.length) {
          blockedQ.push({
            process: current,
            remainingIO: current.bursts[current.index]
          });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        } else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }

        current = null;
      }
    }

    /* BLOCKED → READY */
    let movedBlocked = false;
    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;
      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
        movedBlocked = true;
      } else i++;
    }
    if (movedBlocked) await sleep(150);

    /* NEW → READY */
    let movedNew = false;
    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
        movedNew = true;
      } else i++;
    }
    if (movedNew) await sleep(150);

    /* READY → RUNNING (LJF PICK) */
    if (!current && readyQ.length) {
      readyQ.sort(
        (a, b) => b.bursts[b.index] - a.bursts[a.index]
      );
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}




async function priority_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = []; // { process, remainingIO }
  let current = null;

  /* LOAD ALL INTO NEW */
  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2]
      .querySelector("input")
      .value.split(",")
      .map(v => parseInt(v.trim()))
      .filter(v => !isNaN(v));

    const priority = parseInt(
      row.children[3].querySelector("input").value
    );

    const p = {
      pid,
      arrival,
      bursts,
      priority,   // ⭐ priority included
      index: 0,
      card: createProcessCard(pid)
    };

    newQ.push(p);
    newBox.appendChild(p.card);
  });

  newQ.sort((a, b) => a.arrival - b.arrival);

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    /* 1️⃣ RUNNING EXECUTES */
    if (current) {
      current.bursts[current.index]--;

      if (current.bursts[current.index] === 0) {
        current.index++;

        // CPU → IO
        if (current.index < current.bursts.length) {
          blockedQ.push({
            process: current,
            remainingIO: current.bursts[current.index]
          });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        }
        // DONE
        else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }

        current = null;
      }
    }

    /* 2️⃣ BLOCKED → READY */
    let movedBlocked = false;
    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;

      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
        movedBlocked = true;
      } else i++;
    }
    if (movedBlocked) await sleep(150);

    /* 3️⃣ NEW → READY */
    let movedNew = false;
    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
        movedNew = true;
      } else i++;
    }
    if (movedNew) await sleep(150);

    /* 4️⃣ READY → RUNNING (PRIORITY PICK) */
    if (!current && readyQ.length) {
      // lower priority value = higher priority
      readyQ.sort((a, b) => a.priority - b.priority);

      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}





async function lrtf_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = [];
  let current = null;

  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);
    const bursts = row.children[2].querySelector("input").value
      .split(",").map(v => parseInt(v.trim())).filter(Boolean);

    const p = { pid, arrival, bursts, index: 0, card: createProcessCard(pid) };
    newQ.push(p);
    newBox.appendChild(p.card);
  });

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    if (current) {
      current.bursts[current.index]--;
      if (current.bursts[current.index] === 0) {
        current.index++;
        if (current.index < current.bursts.length) {
          blockedQ.push({ process: current, remainingIO: current.bursts[current.index] });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        } else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }
        current = null;
      }
    }

    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;
      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
      } else i++;
    }

    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
      } else i++;
    }

    if (current) {
      readyQ.sort((a, b) => b.bursts[b.index] - a.bursts[a.index]);
      if (readyQ.length && readyQ[0].bursts[readyQ[0].index] > current.bursts[current.index]) {
        readyQ.push(current);
        readyBox.appendChild(current.card);
        blinkArrow(".arrow-running-ready");
        current = null;
      }
    }

    if (!current && readyQ.length) {
      readyQ.sort((a, b) => b.bursts[b.index] - a.bursts[a.index]);
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}




async function preemptive_priority_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = [];
  let current = null;

  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);
    const bursts = row.children[2].querySelector("input").value
      .split(",").map(v => parseInt(v.trim())).filter(Boolean);
    const priority = parseInt(row.children[3].querySelector("input").value);

    const p = { pid, arrival, bursts, priority, index: 0, card: createProcessCard(pid) };
    newQ.push(p);
    newBox.appendChild(p.card);
  });

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    if (current) {
      current.bursts[current.index]--;
      if (current.bursts[current.index] === 0) {
        current.index++;
        if (current.index < current.bursts.length) {
          blockedQ.push({ process: current, remainingIO: current.bursts[current.index] });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        } else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }
        current = null;
      }
    }

    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;
      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
      } else i++;
    }

    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
      } else i++;
    }

    if (current) {
      readyQ.sort((a, b) => a.priority - b.priority);
      if (readyQ.length && readyQ[0].priority < current.priority) {
        readyQ.push(current);
        readyBox.appendChild(current.card);
        blinkArrow(".arrow-running-ready");
        current = null;
      }
    }

    if (!current && readyQ.length) {
      readyQ.sort((a, b) => a.priority - b.priority);
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}


async function srtf_visualization() {
  clearAllStateBoxes();

  const newBox = document.getElementById("newBox");
  const readyBox = document.getElementById("readyBox");
  const runningBox = document.getElementById("runningBox");
  const blockedBox = document.getElementById("blockedBox");
  const terminatedBox = document.getElementById("terminatedBox");
  const timerEl = document.getElementById("timer");

  let time = 0;
  timerEl.innerText = time;

  let newQ = [];
  let readyQ = [];
  let blockedQ = [];
  let current = null;

  /* LOAD INTO NEW */
  document.querySelectorAll("#processTableBody tr").forEach(row => {
    const pid = row.children[0].innerText.trim();
    const arrival = parseInt(row.children[1].querySelector("input").value);

    const bursts = row.children[2].querySelector("input").value
      .split(",").map(v => parseInt(v.trim())).filter(Boolean);

    const p = { pid, arrival, bursts, index: 0, card: createProcessCard(pid) };
    newQ.push(p);
    newBox.appendChild(p.card);
  });

  while (newQ.length || readyQ.length || blockedQ.length || current) {
    await sleep(1000);

    /* RUNNING executes */
    if (current) {
      current.bursts[current.index]--;

      if (current.bursts[current.index] === 0) {
        current.index++;

        if (current.index < current.bursts.length) {
          blockedQ.push({ process: current, remainingIO: current.bursts[current.index] });
          blockedBox.appendChild(current.card);
          blinkArrow(".arrow-running-blocked");
          current.index++;
        } else {
          terminatedBox.appendChild(current.card);
          blinkArrow(".arrow-running-terminated");
        }
        current = null;
      }
    }

    /* BLOCKED → READY */
    for (let i = 0; i < blockedQ.length; ) {
      blockedQ[i].remainingIO--;
      if (blockedQ[i].remainingIO === 0) {
        const p = blockedQ.splice(i, 1)[0].process;
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-blocked-ready");
      } else i++;
    }

    /* NEW → READY */
    for (let i = 0; i < newQ.length; ) {
      if (newQ[i].arrival <= time) {
        const p = newQ.splice(i, 1)[0];
        readyQ.push(p);
        readyBox.appendChild(p.card);
        blinkArrow(".arrow-new-ready");
      } else i++;
    }

    /* PREEMPTION CHECK */
    if (current) {
      readyQ.sort((a, b) => a.bursts[a.index] - b.bursts[b.index]);
      if (readyQ.length && readyQ[0].bursts[readyQ[0].index] < current.bursts[current.index]) {
        readyQ.push(current);
        readyBox.appendChild(current.card);
        blinkArrow(".arrow-running-ready");
        current = null;
      }
    }

    /* READY → RUNNING */
    if (!current && readyQ.length) {
      readyQ.sort((a, b) => a.bursts[a.index] - b.bursts[b.index]);
      current = readyQ.shift();
      runningBox.appendChild(current.card);
      blinkArrow(".arrow-ready-running");
    }

    time++;
    timerEl.innerText = time;
  }
}
