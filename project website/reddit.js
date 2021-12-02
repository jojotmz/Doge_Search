const btn = document.querySelector('#search-submit');
const field = document.querySelector('#search');

function getResults(query) {
    const url = `http://localhost:8983/solr/workpls/select?indent=true&q.op=OR&q=Keyword%3A${query}%20OR%0APost_Text%3A
    ${query}%20OR%0AComment_1%3A${query}%20OR%0AComment_2%3A${query}%20OR%0AComment_3%3A${query}%20OR%0AComment_4%3A
    ${query}%20OR%0AComment_5%3A${query}&rows=200`;
    console.log(url);
    fetch(url).then(response => {
        response.json().then(myList => {
            let list = myList.response.docs;
            let display = document.getElementById("content");
            let content = `<h3>Found ${list.length} results for: ${field.value}</h3>`;
            for (let i = 0; i < list.length; i++) {
                let it = list[i];
                content += "<details>";
                content += `<summary class="collapsible">${it.Post_Text}</summary>`;
                content += `<p><a href="${it.Post_Url}">${it.Post_Url}</a><br>`;
                content += `<b>${it.Post_Text}</b><br><br>`;
                if (it.Comment_1 !== undefined)
                    content += `<b>Comment 1:</b>${it.Comment_1}<br>`;
                if (it.Comment_2 !== undefined)
                    content += `<b>Comment 2:</b>${it.Comment_2}<br>`;
                if (it.Comment_3 !== undefined)
                    content += `<b>Comment 3:</b>${it.Comment_3}<br>`;
                if (it.Comment_4 !== undefined)
                    content += `<b>Comment 4:</b>${it.Comment_4}<br>`;
                if (it.Comment_5 !== undefined)
                    content += `<b>Comment 5:</b>${it.Comment_5}<br>`;
                content += `<button id="${it.id}">not relevant?</button>
                            <button id="mlt">More like this?</button></p>`;
                content += "</details><br>";
            }
            display.innerHTML = content;

            for (let i = 0; i < list.length; i++) {
                let id = list[i].id;
                document.getElementById(id).onclick = () => {
                    let newQuery = query + " -id:" + list[i].id;
                    console.log(query, newQuery);
                    getResults(newQuery);
                }
            }

            document.getElementById('mlt').onclick = () => {
                let newUrl = `http://localhost:8983/solr/greddit/select?indent=true&q.op=OR&q=Keyword%3A${query}
                %20OR%0ADescription%3A${query}`;
                fetch(newUrl).then(response => {
                    response.json().then(myList => {
                        let list = myList.response.docs;
                        let display = document.getElementById("content");
                        let content = `<h3>Found more ${list.length} results for: ${field.value}</h3>`;
                        for (let i = 0; i < list.length; i++) {
                            let it = list[i];
                            content += "<div>";
                            content += `<p><a href="${it.Link}">${it.Link}</a><br>`;
                            if (it.Description !== undefined)
                                content += `${it.Description}<br></p>`;
                            else
                                content += `Description Unavailable<br></p>`;
                            content += "</div>";
                        }
                        display.innerHTML = content;
                    })
                })
            }
        }).catch(console.error);
    })
}


btn.addEventListener('click', () => {
    const query = encodeURIComponent(field.value);
    console.log(query);
    getResults(query);
});