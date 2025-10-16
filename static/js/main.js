const uploadForm = document.getElementById("uploadForm");
const contextInput = document.getElementById("contextInput");
const saveContextBtn = document.getElementById("saveContext");
const generateBtn = document.getElementById("generateInsights");
const outputDiv = document.getElementById("output");

// ---- Upload Data ----
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(uploadForm);
  const res = await fetch("/upload-data", { method: "POST", body: formData });
  const data = await res.json();
  outputDiv.innerText = JSON.stringify(data, null, 2);
});

// ---- Save Context ----
saveContextBtn.addEventListener("click", async () => {
  const context = { text: contextInput.value };
  const res = await fetch("/update-context", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(context),
  });
  const data = await res.json();
  outputDiv.innerText = JSON.stringify(data, null, 2);
});

// ---- Generate Insights ----
generateBtn.addEventListener("click", async () => {
  outputDiv.innerHTML = "";
  outputDiv.classList.add("loading");

  const eventSource = new EventSource("/generate-insights", { withCredentials: false });

  eventSource.onmessage = (event) => {
    const data = event.data;
    let typeClass = "";

    if (data.startsWith("THINK:")) typeClass = "think";
    else if (data.startsWith("SEARCH:")) typeClass = "search";
    else if (data.startsWith("ACT:")) typeClass = "act";
    else if (data.startsWith("INSIGHT:") || data.startsWith("Final Insight:")) typeClass = "insight";
    else if (data.startsWith("Error")) typeClass = "error";

    // Create collapsible step block
    const stepBlock = document.createElement("div");
    stepBlock.className = "step-block";

    const header = document.createElement("div");
    header.className = `step-header ${typeClass}`;
    header.innerText = data.split("\n")[0];
    stepBlock.appendChild(header);

    const content = document.createElement("div");
    content.className = "step-content";
    content.innerText = data.split("\n").slice(1).join("\n") || "[No details]";
    stepBlock.appendChild(content);

    header.addEventListener("click", () => {
      content.style.display = content.style.display === "none" ? "block" : "none";
    });

    outputDiv.appendChild(stepBlock);
    outputDiv.scrollTop = outputDiv.scrollHeight;
  };

  eventSource.onerror = () => {
    outputDiv.classList.remove("loading");
    const div = document.createElement("div");
    div.className = "error";
    div.innerText = "[Stream ended or error occurred]";
    outputDiv.appendChild(div);
    eventSource.close();
    outputDiv.scrollTop = outputDiv.scrollHeight;
  };
});
