document.addEventListener("DOMContentLoaded", function () {
    console.log("Script yüklendi!");

    let movieSelect = document.getElementById("movies");
    let submitButton = document.querySelector("button");
    let selectedMoviesList = document.getElementById("selected-movies-list");

    // Seçilen filmleri saklamak için bir Array
    let selectedMovies = [];

    if (movieSelect && submitButton && selectedMoviesList) {
        updateSubmitButton();
        updateSelectedMovies();

        // Kullanıcı her yeni film seçtiğinde listeyi güncelle
        movieSelect.addEventListener("change", function () {
            addSelectedMovies();
            updateSubmitButton();
        });
    }
    let likedMovies = [];

    function toggleLike(movieId, action) {
    // Eğer film daha önce beğenildiyse çıkar, beğenilmediyse ekle
    const index = likedMovies.indexOf(movieId);
    
    if (action === 'liked') {
        if (index === -1) {
            likedMovies.push(movieId); // Beğenildiğinde ekle
        }
    } else if (action === 'disliked') {
        if (index !== -1) {
            likedMovies.splice(index, 1); // Beğenilmediğinde çıkar
        }
    }
    
    // Beğenilen film ID'lerini formda gizli alanlara aktar
    document.getElementById('liked_movie_ids').value = likedMovies.join(',');
    document.getElementById('movie_ids').value = movieId;
    }
    function addSelectedMovies() {
        let selectedOptions = Array.from(movieSelect.selectedOptions);

        // Yeni seçilen filmleri diziye ekleyelim (Eğer zaten eklenmemişse)
        selectedOptions.forEach(option => {
            if (!selectedMovies.includes(option.value)) {
                selectedMovies.push(option.value); // Listeye ekle
                addMovieToList(option.value); // Listeyi güncelle
            }
        });

        updateSelectedMovies(); // Listeyi güncelle
    }

    function addMovieToList(movie) {
        let li = document.createElement("li");
        li.textContent = movie;
        li.style.display = "flex";
        li.style.justifyContent = "space-between";
        li.style.alignItems = "center";
        li.style.padding = "10px";
        li.style.background = "#fff";
        li.style.marginBottom = "5px";
        li.style.borderRadius = "5px";
        li.style.boxShadow = "0px 0px 5px rgba(0,0,0,0.1)";
        li.style.fontSize = "16px";

        // ❌ Butonu ile film kaldırma özelliği
        let removeButton = document.createElement("button");
        removeButton.textContent = "❌";
        removeButton.style.marginLeft = "10px";
        removeButton.style.backgroundColor = "darkred";
        removeButton.style.color = "white";
        removeButton.style.border = "none";
        removeButton.style.padding = "5px";
        removeButton.style.borderRadius = "3px";
        removeButton.style.cursor = "pointer";

        removeButton.onclick = function () {
            let index = selectedMovies.indexOf(movie);
            if (index > -1) {
                selectedMovies.splice(index, 1); // Listeden kaldır
            }
            li.remove(); // HTML'den de kaldır
            updateSubmitButton();
        };

        li.appendChild(removeButton);
        selectedMoviesList.appendChild(li);
    }

    function updateSelectedMovies() {
        // Eğer film seçilmediyse kutucuğu temizle
        if (selectedMovies.length === 0) {
            selectedMoviesList.innerHTML = "";
        }
    }

    function updateSubmitButton() {
        submitButton.disabled = selectedMovies.length === 0;
    }
});
