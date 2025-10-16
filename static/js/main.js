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

  let currentStepBlock = null;
  let currentAction = null;

  const eventSource = new EventSource("/generate-insights", { withCredentials: false });

  eventSource.onmessage = (event) => {
    const data = event.data.trim();
    
    // Parse the structured output format
    if (data.startsWith("STEP:")) {
      // New step started
      const stepNum = data.split(":")[1].trim();
      currentStepBlock = document.createElement("div");
      currentStepBlock.className = "step-block";
      
      const header = document.createElement("div");
      header.className = "step-header";
      header.innerText = `Step ${stepNum}`;
      
      const content = document.createElement("div");
      content.className = "step-content";
      content.style.display = "block"; // Show by default
      
      header.addEventListener("click", () => {
        content.style.display = content.style.display === "none" ? "block" : "none";
      });
      
      currentStepBlock.appendChild(header);
      currentStepBlock.appendChild(content);
      outputDiv.appendChild(currentStepBlock);
      currentAction = null;
      
    } else if (data.startsWith("THINK:")) {
      // THINK action
      currentAction = "think";
      const thinkContent = data.substring(6).trim();
      addActionOutput("THINK", thinkContent, "think", currentStepBlock);
      
    } else if (data.startsWith("SEARCH:")) {
      // SEARCH action
      currentAction = "search";
      const searchContent = data.substring(7).trim();
      addActionOutput("SEARCH", searchContent, "search", currentStepBlock);
      
    } else if (data.startsWith("ACT:")) {
      // ACT action
      currentAction = "act";
      const actContent = data.substring(4).trim();
      addActionOutput("ACT", actContent, "act", currentStepBlock);
      
    } else if (data.startsWith("INSIGHT:")) {
      // INSIGHT from ACT
      currentAction = "insight";
      const insightContent = data.substring(8).trim();
      addActionOutput("INSIGHT", insightContent, "insight", currentStepBlock);
      
    } else if (data.startsWith("EVALUATION:")) {
      // Evaluation result
      const evalContent = data.substring(11).trim();
      addActionOutput("EVALUATION", evalContent, "evaluation", currentStepBlock);
      
    } else if (data.startsWith("FINAL:")) {
      // Final summary section
      currentStepBlock = document.createElement("div");
      currentStepBlock.className = "step-block final-block";
      
      const header = document.createElement("div");
      header.className = "step-header insight";
      header.innerText = "Final Summary";
      
      const content = document.createElement("div");
      content.className = "step-content";
      content.style.display = "block";
      
      currentStepBlock.appendChild(header);
      currentStepBlock.appendChild(content);
      outputDiv.appendChild(currentStepBlock);
      
    } else if (data.startsWith("Final Insight:")) {
      // Final insight content
      const finalContent = data.substring(14).trim();
      if (currentStepBlock && currentStepBlock.classList.contains("final-block")) {
        const content = currentStepBlock.querySelector(".step-content");
        const p = document.createElement("p");
        p.className = "insight";
        p.innerText = finalContent;
        content.appendChild(p);
      }
      
    } else if (data.startsWith("ERROR:")) {
      // Error message
      const errorContent = data.substring(6).trim();
      addActionOutput("ERROR", errorContent, "error", currentStepBlock);
      
    } else if (data && currentStepBlock) {
      // Continuation of previous content
      const content = currentStepBlock.querySelector(".step-content");
      if (content && content.lastChild) {
        content.lastChild.innerText += "\n" + data;
      }
    }
    
    outputDiv.scrollTop = outputDiv.scrollHeight;
  };

  eventSource.onerror = () => {
    outputDiv.classList.remove("loading");
    const div = document.createElement("div");
    div.className = "error";
    div.innerText = "[Stream ended]";
    outputDiv.appendChild(div);
    eventSource.close();
    outputDiv.scrollTop = outputDiv.scrollHeight;
  };
});

function addActionOutput(label, content, cssClass, parentBlock) {
  if (!parentBlock) return;
  
  const contentDiv = parentBlock.querySelector(".step-content");
  if (!contentDiv) return;
  
  const actionDiv = document.createElement("div");
  actionDiv.className = `action-output ${cssClass}`;
  
  const labelSpan = document.createElement("strong");
  labelSpan.innerText = label + ": ";
  
  const contentSpan = document.createElement("span");
  contentSpan.innerText = content;
  
  actionDiv.appendChild(labelSpan);
  actionDiv.appendChild(contentSpan);
  contentDiv.appendChild(actionDiv);
}