(function(){
    // 현재 페이지 URL 획득
    const currentUrl = window.location.href;
    
    // 백엔드의 /recommendations 엔드포인트 호출
    fetch("http://localhost:8000/ai/recommendations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: currentUrl })
    })
    .then(response => response.json())
    .then(data => {
        const recommendations = data.content;

        if (Array.isArray(recommendations) && recommendations.length > 0) {
            // 추천 결과 오버레이 생성
            const overlay = document.createElement("div");
            overlay.id = "harry-overlay";
            overlay.style.position = "fixed";
            overlay.style.top = "10px";
            overlay.style.right = "10px";
            overlay.style.width = "300px";
            overlay.style.backgroundColor = "rgba(255,255,255,0.9)";
            overlay.style.border = "1px solid #ccc";
            overlay.style.padding = "10px";
            overlay.style.zIndex = "9999";
            overlay.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
            overlay.style.fontFamily = "Arial, sans-serif";
            overlay.style.fontSize = "14px";
            overlay.innerHTML = "<h3>관련 페이지 추천</h3>";

            recommendations.forEach(item => {
                const recDiv = document.createElement("div");
                recDiv.style.marginBottom = "10px";
                recDiv.style.cursor = "pointer";

                // 썸네일 이미지
                const img = document.createElement("img");
                img.src = item.thumbnail;
                img.alt = item.title;
                img.style.width = "100%";
                img.style.height = "auto";
                recDiv.appendChild(img);

                // 제목 표시
                const titleEl = document.createElement("div");
                titleEl.textContent = item.title;
                titleEl.style.fontWeight = "bold";
                titleEl.style.marginTop = "5px";
                recDiv.appendChild(titleEl);

                // 클릭 시 새 탭에서 링크 열기
                recDiv.addEventListener("click", function(){
                    window.open(item.link, "_blank");
                });

                overlay.appendChild(recDiv);
            });

            document.body.appendChild(overlay);
        }
    })
    .catch(err => console.error("harry recommendation error:", err));
})();
