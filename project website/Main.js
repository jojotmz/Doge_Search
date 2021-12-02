const btn = document.querySelector('#search-submit');
const field = document.querySelector('#search');
let b_list = new Map();

function getResults(query) {
    if (!b_list.has(query)) {
    const url = `http://localhost:8983/solr/quora/select?indent=true&q.op=OR&q=Comment_5%3A
    ${query}%20OR%0AComment_4%3A${query}%20OR%0AComment_3%3A${query}%20OR%0AComment_2%3A${query}%20OR%0AComment_1%3A
    ${query}%20OR%0APost_Text%3A${query}&rows=200`;
    console.log(url);
    fetch(url).then(response => {
        response.json().then(myList => {
            let list = myList.response.docs;
            let display = document.getElementById("content");
            let content = `<h3>Found ${list.length} results for: ${field.value}</h3>`;
            for (let i = 0; i < list.length; i++) {
                let it = list[i];
                content += "<details>";
                content += `<summary class="collapsible">${it.Post_Title}</summary>`;
                content += `<p><a href="${it.Post_Url}">${it.Post_Url}</a><br><br>`;
                content += `<b>${it.Post_Title}</b><br>`;
                content += `${it.Post_Text}<br><br>`;
                if (it.Comment_1 !== undefined)
                 content += `<b>Answer 1: </b>${it.Comment_1}<br>`;
                if (it.Comment_2 !== undefined)
                    content += `<b>Answer 2: </b>${it.Comment_2}<br>`;
                if (it.Comment_3 !== undefined)
                    content += `<b>Answer 3: </b>${it.Comment_3}<br>`;
                if (it.Comment_4 !== undefined)
                    content += `<b>Answer 4: </b>${it.Comment_4}<br>`;
                if (it.Comment_5 !== undefined)
                    content += `<b>Answer 5: </b>${it.Comment_5}<br>`;
                content += `<button id="${it.id}">Not relevant?</button>
                            <button id="${i}">More like this?</button></p>`;
                content += "</details><br>";
            }
            display.innerHTML = content;

            for (let i = 0; i < list.length; i++) {
                let id = list[i].id;
                document.getElementById(id).onclick = () => {
                    let newQuery = query + " -id:" + list[i].id;
                    b_list.set(query, newQuery);
                    console.log(query, newQuery);
                    getResults(newQuery);
                }
            }

            for (let i = 0; i < list.length; i++) {
                document.getElementById(i).onclick = () => {
                const newUrl = `http://localhost:8983/solr/quora/select?defType=edismax&q=keyword%3A${query}^20+
                %20OR%0APost_Text%3A${query}^20.0+%20OR%0AComment_1%3A${query}^20+%20OR%0AComment_2%3A${query}
                %20OR%0AComment_3%3A${query}%20OR%0AComment_4%3A${query}%20OR%0AComment_5%3A${query}&rows=200`;
                fetch(newUrl).then(response => {
                    response.json().then(myList => {
                        let list = myList.response.docs;
                        let display = document.getElementById("content");
                        let content = `<h3>Found ${list.length} results for: ${field.value}</h3>`;
                        for (let i = 0; i < list.length; i++) {
                            let it = list[i];
                            content += "<details>";
                            content += `<summary class="collapsible">${it.Post_Title}</summary>`;
                            content += `<p><a href="${it.Post_Url}">${it.Post_Url}</a><br><br>`;
                            content += `<b>${it.Post_Title}</b><br>`;
                            content += `${it.Post_Text}<br><br>`;
                            if (it.Comment_1 !== undefined)
                                content += `<b>Answer 1: </b>${it.Comment_1}<br>`;
                            if (it.Comment_2 !== undefined)
                                content += `<b>Answer 2: </b>${it.Comment_2}<br>`;
                            if (it.Comment_3 !== undefined)
                                content += `<b>Answer 3: </b>${it.Comment_3}<br>`;
                            if (it.Comment_4 !== undefined)
                                content += `<b>Answer 4: </b>${it.Comment_4}<br>`;
                            if (it.Comment_5 !== undefined)
                                content += `<b>Answer 5: </b>${it.Comment_5}<br>`;
                            content += "</details><br>";
                        }
                        display.innerHTML = content;
                    })
                })
            }}
        })
    }).catch(console.error);
} else {
        getResults(b_list.get(query))
    }}
btn.addEventListener('click', () => {
    const query = encodeURIComponent(field.value);
    console.log(query);
    getResults(query);
});