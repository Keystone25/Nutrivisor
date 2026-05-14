const newsContainer = document.getElementById("news");

window.addEventListener("DOMContentLoaded", () => {

  fetch('https://newsdata.io/api/1/latest?apikey=pub_7f4a59bfb11640358b4d9f5587acd24d&country=in&language=en,ml&category=health,food&image=1&removeduplicate=1')
    .then(response => response.json())
    .then(data => {

      newsContainer.innerHTML = "";

      if (!data.results || data.results.length === 0) {
        newsContainer.innerHTML = "<p>No fitness/health news found.</p>";
        return;
      }

      data.results.forEach(article => {

        const image = article.image_url 
          ? article.image_url 
          : "https://via.placeholder.com/400x200";

        const description = article.description 
          ? article.description 
          : "No description available.";

        const link = article.link;

        const newsCard = document.createElement("div");
        newsCard.className = "news-item";

        newsCard.innerHTML = `
          <img src="${image}" alt="news">
          
          <h4>${article.title}</h4>
          
          <p>${description}</p>
          
          <a href="${link}" target="_blank" class="read-btn">Read More →</a>
        `;

        newsContainer.appendChild(newsCard);
      });

    })
    .catch(error => {
      console.error(error);
      newsContainer.innerHTML = "<p>Failed to load news</p>";
    });

});