const Sort = {
    BY_LIKES: "likes",
    BY_VIEWERS: "viewers",
    BY_DATE: "date",
};

let sortMode = Sort.BY_LIKES
let trashMode = false

// index.html 의 로드가 완료되면 ready(...) 안에 등록된 함수가 자동으로 호출됩니다.
// 아래는 함수에 이름을 부여하지 않고 바로 ready(...) 의 매개변수로 함수를 전달하는 방식으로 로드 완료시 호출될 함수를 등록합니다.
$(document).ready(function () {
    // 영화 목록을 보여줍니다.
    showMovie()

    // 현재 적용되고 있는 정렬 방식의 버튼에 눌려져 보이는 효과를 줍니다.
    displaySorter()

    // 휴지통 모드에 따라 메뉴를 다르게 바꿔줍니다.
    displayTrashMode(trashMode)
});

function showMovie() {
    // 1. id="movie-box" 로 된 태그의 내부 html 태그를 모두 삭제합니다.
    $('#movie-box').empty()

    // 2. sortMode와 휴지통을 보고 있는지 여부를 API(GET /api/movieList)에 실어 호출합니다.
    $.ajax({
        type: "GET",
        url: `/api/movie/list?sortMode=${sortMode}&trashMode=${trashMode}`,
        success: function (response) {
            if (response['result'] != 'success') {
                alert(sortMode + ' 순으로 영화 목록 받아오기 실패!')
                return
            }

            // 3. 서버가 돌려준 movies_list를 이용해 영화 카드를 추가합니다.
            // 이 때 휴지통 여부에 따라 카드 모양이 달라지므로 휴지통 여부(=false)도 같이 전달합니다.
            addMovieCards(response['movies_list'], trashMode)
        }
    })
}

function addMovieCards(movies, trashMode) {
    // for 문을 활용하여 movies 배열의 요소를 차례대로 조회합니다.
    for (let i = 0; i < movies.length; i++) {
        let movie = movies[i]

        // 1. movie[i] 요소의 title,viewers, likes 키 값을 활용하여 값을 조회합니다.
        let id = movie['_id']
        let title = movie['title']
        let viewers = movie['viewers'].toLocaleString()
        let likes = movie['likes']
        let poster_url = movie['poster_url']
        let info_url = movie['info_url']
        let movie_date = movie['open_year'] + '.' + String(movie['open_month']).padStart(2, '0') + '.' + String(movie['open_day']).padStart(2, '0')

        // 2. 영화 카드를 만듭니다.
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

        // 3. 휴지통을 보고 있는지 여부에 따라 카드의 버튼을 다르게 설정해줍니다.
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

        // 4. #movie-box에 생성된 HTML 을 붙입니다.
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

///////////////////////////////////////////////////////////////////////////////
// 주의: 아래 like movie 는 임의의 영화에 좋아요가 표시됩니다.
// 이 구현을 선택한 무비에 좋아요를 넣는 것으로 수정하셔야 됩니다. (함수 매개변수 및 함수 구현 모두)
function likeMovie(movie_id) {
    $.ajax({
        type: "POST",
        url: "/api/movie/like",
        data: { _id: movie_id },
        success: function (response) {
            if (response['result'] == 'success') {
                // 2. '좋아요 완료!' 얼럿을 띄웁니다.
                alert('좋아요 완료!')

                // 3. 변경된 정보를 반영하기 위해 새로고침합니다.
                showMovie()
            } else {
                alert('좋아요 실패ㅠㅠ')
            }
        }
    });
}

function controlMovieTrash(movie_id) {
    // 휴지통 보내기 기능 구현 및 서버 측에 API 추가 후 여기서 그 API 를 호출
    $.ajax({
        type: "POST",
        url: "/api/movie/controlTrash",
        data: { _id: movie_id, trashed: trashMode },
        success: function (response) {
            if (response['result'] == 'success') {
                if (trashMode) {
                    // 2-1. 휴지통 상태라면 '휴지통에서 복구 완료!' alert을 띄웁니다.
                    alert('휴지통에서 복구 완료!')
                } else {
                    // 2-2. 휴지통 상태가 아니라면 '휴지통 보내기 완료!' alert을 띄웁니다.
                    alert('휴지통 보내기 완료!')
                }

                // 3. 변경된 정보를 반영하기 위해 새로고침합니다.
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
    // 휴지통에서 아주 삭제 기능 구현 및 서버 측에 API 를 추가 후 여기서 그 API 를 호출
    $.ajax({
        type: "POST",
        url: "/api/movie/delete",
        data: { _id: movie_id },
        success: function (response) {
            if (response['result'] == 'success') {
                // 2. '삭제 완료! 안녕!' 얼럿을 띄웁니다.
                alert('삭제 완료! 안녕!')
                // 3. 변경된 정보를 반영하기 위해 새로고침합니다.
                showMovie()
            } else {
                alert('아주 삭제 실패ㅠㅠ')
            }
        }
    });
}

// 정렬 기준 버튼을 클릭하면 호출됨
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

// 정렬 기준에 따라 해당 버튼만 활성화 시키고 다른 버튼은 비활성화 시킴
function displaySorter() {
    document.getElementById("sorter-likes").classList.remove("active")
    document.getElementById("sorter-viewers").classList.remove("active")
    document.getElementById("sorter-date").classList.remove("active")

    switch (sortMode) {
        case Sort.BY_LIKES:
            document.getElementById("sorter-likes").classList.add("active")
            break
        case Sort.BY_VIEWERS:
            document.getElementById("sorter-viewers").classList.add("active")
            break
        case Sort.BY_DATE:
            document.getElementById("sorter-date").classList.add("active")
            break
    }
}

function displayTrashMode(trashMode) {
    // trashMode 에 따라 "휴지통 보기" 또는 "휴지통 나가기" 가 출력 되게 구현해야 됩니다.
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