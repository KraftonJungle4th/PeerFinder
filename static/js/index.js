const Sort = {
    BY_LIKES: "likes",
    BY_VIEWERS: "viewers",
    BY_DATE: "date",
};

let sortMode = Sort.BY_LIKES
let trashMode = false

// index.html 의 로드가 완료되면 ready(...) 안에 등록된 함수가 자동 호출
// 아래는 함수에 이름을 부여하지 않고 바로 ready(...) 의 매개변수로 함수를 전달하는 방식으로 로드 완료시 호출될 함수를 등록합니다.
$(document).ready(function () {
    showMovie()

    // 현재 적용되고 있는 정렬 방식의 버튼에 눌려져 보이는 효과 적용
    displaySorter()

    // 휴지통 모드에 따라 메뉴 변경
    displayTrashMode(trashMode)
});

function showMovie() {
    $('#movie-box').empty()

    // sortMode와 휴지통 여부를 API(GET /api/movie/list)에 실어 호출
    $.ajax({
        type: "GET",
        url: `/api/movie/list?sortMode=${sortMode}&trashMode=${trashMode}`,
        success: function (response) {
            if (response['result'] != 'success') {
                alert(sortMode + ' 순으로 영화 목록 받아오기 실패!')
                return
            }

            // 서버가 돌려준 movies_list를 이용해 영화 카드 추가
            // 휴지통 여부에 따라 카드 모양이 달라지므로 휴지통 여부(=false)도 같이 전달
            addMovieCards(response['movies_list'], trashMode)
        }
    })
}

function addMovieCards(movies, trashMode) {
    // for 문을 활용하여 movies 배열의 요소를 차례대로 조회
    for (let i = 0; i < movies.length; i++) {
        let movie = movies[i]

        // movie[i] 요소의 title,viewers, likes 키 값을 활용하여 값을 조회
        let id = movie['_id']
        let title = movie['title']
        let viewers = movie['viewers'].toLocaleString()
        let likes = movie['likes']
        let poster_url = movie['poster_url']
        let info_url = movie['info_url']
        let movie_date = movie['open_year'] + '.' + String(movie['open_month']).padStart(2, '0') + '.' + String(movie['open_day']).padStart(2, '0')

        let cardPosterHtml = `<img src="${poster_url}" alt="${movie['title']} 포스터"/>`;
        let cardContentHtml =
            `<div class="d-flex flex-column mb-3">
                <span>
                    <a href=${info_url} class="h4 movie-title">${title}</a>
                </span>
                <span class="movie-likes">
                    <span class="icon"><i class="fas fa-thumbs-up"></i></span>${likes}
                </span>
                <span class="movie-viewers">누적관객수 ${viewers} 명</span>
                <span class="movie-date">개봉일 ${movie_date}</span>
            </div>`

        let cardFooterHtml = ''

        if (trashMode == false) {
            cardFooterHtml =
                `<a href="#" class="movie-button1 p-2 flex-fill movie-button-left" onclick="likeMovie('${id}')">
                    위로! <span class="icon"><i class="fas fa-thumbs-up"></i></span>
                </a>
                <a href="#" class="movie-button2 p-2 flex-fill movie-button-right" onclick="controlMovieTrash('${id}')">
                    휴지통으로 <span class="icon"><i class="fas fa-trash"></i></span>
                </a>`
        } else {
            cardFooterHtml =
                `<a href="#" class="movie-button3 p-2 flex-fill movie-button-left" onclick="controlMovieTrash('${id}')">
                    복구하기 <span class="icon"><i class="fas fa-trash-restore"></i></span>
                </a>
                <a href="#" class="movie-button4 p-2 flex-fill movie-button-right" onclick="deleteMovie('${id}')">
                    영구삭제 <span class="icon"><i class="fas fa-trash-alt"></i></span>
                </a>`
        }

        // 4. #movie-box에 생성된 HTML 부착
        $('#movie-box').append(
            `<div class="shadow-lg card mb-3">
                <div class="row g-0">
                    <div class="col-md-2 m-3">
                        ${cardPosterHtml}
                    </div>    
                    <div class="col-md-9 mt-3">
                        ${cardContentHtml}
                    </div>
                </div>
                <div class="d-flex center">
                    ${cardFooterHtml}
                </div>
            </div>`)
    }
}

function likeMovie(movie_id) {
    $.ajax({
        type: "POST",
        url: "/api/movie/like",
        data: { _id: movie_id },
        success: function (response) {
            if (response['result'] == 'success') {
                alert('좋아요 완료!')
                showMovie()
            } else {
                alert('좋아요 실패ㅠㅠ')
            }
        }
    });
}

function controlMovieTrash(movie_id) {
    // 휴지통 보내기 기능 구현
    $.ajax({
        type: "POST",
        url: "/api/movie/controlTrash",
        data: { _id: movie_id, trashed: trashMode },
        success: function (response) {
            if (response['result'] == 'success') {
                if (trashMode) {
                    alert('휴지통에서 복구 완료!')
                } else {
                    alert('휴지통 보내기 완료!')
                }

                showMovie()
            } else {
                if (trashMode) {
                    alert('휴지통에서 복구 실패ㅠㅠ')
                } else {
                    alert('휴지통 보내기 실패ㅠㅠ')
                }
            }
        }
    });
}

function deleteMovie(movie_id) {
    // 휴지통에서 아주 삭제 기능 구현
    $.ajax({
        type: "POST",
        url: "/api/movie/delete",
        data: { _id: movie_id },
        success: function (response) {
            if (response['result'] == 'success') {
                alert('삭제 완료! 안녕!')
                showMovie()
            } else {
                alert('아주 삭제 실패ㅠㅠ')
            }
        }
    });
}

// 정렬 기준 버튼을 클릭하면 호출
function changeSorter(newMode) {
    if (sortMode == newMode) {
        return
    }

    sortMode = newMode
    displaySorter()
    showMovie()
}

function changeTrashMode() {
    trashMode = !trashMode
    displayTrashMode(trashMode)
    showMovie()
}

// 정렬 기준에 따라 해당 버튼만 활성화 시키고 다른 버튼은 비활성화
function displaySorter() {
    const sorterLikes = document.getElementById("sorter-likes");
    const sorterViewers = document.getElementById("sorter-viewers");
    const sorterDate = document.getElementById("sorter-date");

    // 모든 버튼의 'active' 클래스를 제거
    [sorterLikes, sorterViewers, sorterDate].forEach(button => button.classList.remove("active"));

    // 현재 정렬 기준에 따라 해당 버튼에 'active' 클래스 추가
    switch (sortMode) {
        case Sort.BY_LIKES:
            sorterLikes.classList.add("active");
            break;
        case Sort.BY_VIEWERS:
            sorterViewers.classList.add("active");
            break;
        case Sort.BY_DATE:
            sorterDate.classList.add("active");
            break;
    }
}


// trashMode 에 따라 "휴지통 보기" 또는 "휴지통 나가기" 가 출력
function displayTrashMode(trashMode) {
    $("#trash-mode-box").empty()

    let tempStatus = trashMode
        ? `<span class="icon"><i class="fas fa-trash-restore"></i></span> 휴지통 나가기`
        : `<span class="icon"><i class="fas fa-trash"></i></span> 휴지통 보기`;
    let tempHtml =
        `<div>
            <a href="#" class="trash-mode-box" onclick="changeTrashMode()">
                ${tempStatus}
            </a>
        </div>`;

    $("#trash-mode-box").append(tempHtml)
}