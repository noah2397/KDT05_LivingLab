// 주기적으로 파일 내용을 요청하는 함수
function fetchFileContent() {
  fetch("/get_file_content")
    .then((response) => response.json())
    .then((data) => {
      var outputDiv = document.getElementById("command-output");
      outputDiv.innerHTML = data.content.replace(/([.!?])/g, "$1<br>");
      outputDiv.scrollTop = outputDiv.scrollHeight;
    })
    .catch((error) => console.error("Error fetching file content:", error));
}

setInterval(fetchFileContent, 300);
