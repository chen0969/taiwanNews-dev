fetch('data/news.json')
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('news-container');
        container.innerHTML = '';

        // 整理資料：以日期分組
        const grouped = {};
        data.articles.forEach(article => {
          const date = article.date || '未知日期';
          if (!grouped[date]) grouped[date] = [];
          grouped[date].push(article);
        });

        // 把每個日期段落加到 HTML
        const dates = Object.keys(grouped).sort((a, b) => b.localeCompare(a)); // 最新在上
        dates.forEach(date => {
          const section = document.createElement('section');
          const title = document.createElement('h2');
          title.textContent = date;
          section.appendChild(title);

          const ul = document.createElement('ul');
          grouped[date].forEach(article => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = article.url;
            a.textContent = article.title;
            a.target = "_blank";
            li.appendChild(a);
            ul.appendChild(li);
          });

          section.appendChild(ul);
          container.appendChild(section);
        });
      })
      .catch(err => {
        const container = document.getElementById('news-container');
        container.innerHTML = '<p>❌ 無法載入新聞資料，請稍後再試。</p>';
        console.error(err);
      });