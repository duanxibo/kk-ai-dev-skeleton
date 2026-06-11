const tasks = [
  { title: "编写 requirement brief", status: "done" },
  { title: "实现任务看板筛选", status: "open" },
  { title: "补充部署检查清单", status: "open" },
  { title: "记录 QA evidence", status: "done" },
];

const statusLabels = {
  open: "待完成",
  done: "已完成",
};

const searchInput = document.querySelector("#search");
const statusSelect = document.querySelector("#status");
const taskList = document.querySelector("#tasks");
const count = document.querySelector("#count");
const empty = document.querySelector("#empty");

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const status = statusSelect.value;
  const visible = tasks.filter((task) => {
    const queryMatches = task.title.toLowerCase().includes(query);
    const statusMatches = status === "all" || task.status === status;
    return queryMatches && statusMatches;
  });

  taskList.innerHTML = "";
  visible.forEach((task) => {
    const item = document.createElement("li");
    const title = document.createElement("span");
    const badge = document.createElement("span");
    title.textContent = task.title;
    badge.className = `badge ${task.status}`;
    badge.textContent = statusLabels[task.status] || task.status;
    item.append(title, badge);
    taskList.append(item);
  });

  count.textContent = `当前显示 ${visible.length} 个任务`;
  empty.hidden = visible.length > 0;
}

searchInput.addEventListener("input", render);
statusSelect.addEventListener("change", render);
render();
