function getQueryStringByFilters() {
  var arrDist = $('input:checkbox[name=checkDist]:checked').map(function() {
    return Number(this.value);
  }).get();
  var arrRoom = $('input:checkbox[name=checkRoom]:checked').map(function() {
    return Number(this.value);
  }).get();
  var price_min = $("#price_min").val();
  var price_max = $("#price_max").val();
  var description = $("#description").val();
  var sort = $('input[name=sortRadios]:checked').val()

  var queryData = {
    'districts': arrDist,
    'rooms_count': arrRoom,
    'price_min': price_min,
    'price_max': price_max,
    'description': description,
    'sort': sort,
    'page': 0,
  };
  var query_string = "?" + $.param(queryData, true);
  return query_string
}

function insertElements(parentID, childClass, elements, templateFunc) {
  var container = document.getElementById(parentID);
  container.innerHTML = "";

  elements.forEach(function(element) {
    var child = document.createElement('div');
    child.className = childClass;
    child.innerHTML = templateFunc(element);
    container.appendChild(child); 
  })
}

function insertDistricts() {
  var elements = [
    [0, 'Борщаговка'],
    [1, 'Голосеевский'],
    [2, 'Дарницкий'],
    [3, 'Деснянский'],
    [4, 'Днепровский'],
    [5, 'Оболонский'],
    [6, 'Печерский'],
    [7, 'Подольский'],
    [8, 'Святошинский'],
    [9, 'Соломенский'],
    [10, 'Троещина'],
    [11, 'Шевченковский'],
  ];

  function template(element) {
    var template = `
      <input type="checkbox" class="custom-control-input" id="checkDist${element[0]}" name="checkDist" value=${element[0]}>
      <label class="custom-control-label" for="checkDist${element[0]}">${element[1]}</label>
    `;
    return template;
  }
  insertElements(
    parentID='districts',
    childClass='custom-control custom-checkbox',
    elements=elements,
    templateFunc=template
  );
}

function insertRoomsCount() {
  var elements = [1,2,3,4,5,6,7,8,9];
  function template(element) {
    var template = `
      <input class="form-check-input custom-control-input" type="checkbox" id="checkRoom${element}" name="checkRoom" value=${element}>
      <label class="custom-control-label" for="checkRoom${element}">${element}</label>
    `;
    return template;
  }
  insertElements(
    parentID='roomsCount',
    childClass='form-check form-check-inline',
    elements=elements,
    templateFunc=template
  );
}

function insertSorting() {
  var elements = [
    ['sc_d', 'по релевантности вниз'],
    ['sc_a', 'по релевантности вверх'],
    ['pd_d', 'по дате публикации вниз'],
    ['pd_a', 'по дате публикации вверх'],
    ['pr_d', 'по цене вниз'],
    ['pr_a', 'по цене вверх']
  ];
  function template(element) {
    var template = `
      <input class="form-check-input" type="radio" name="sortRadios" id="sortRadios${element[0]}" value="${element[0]}">
      <label class="form-check-label" for="exampleRadios${element[0]}">${element[1]}</label>
    `;
    return template;
  }
  insertElements(
    parentID='sorting',
    childClass='form-check form-check-inline',
    elements=elements,
    templateFunc=template
  );
}

function setFilters(filters) {
  // console.log('setFilters', filters)
  if (filters.districts) {
    filters.districts.forEach(function(id) {
      document.getElementById(`checkDist${id}`).checked = true;
    })
  }
  if (filters.rooms_count) {
    filters.rooms_count.forEach(function(id) {
      document.getElementById(`checkRoom${id}`).checked = true;
    })
  }
  if (filters.description) {
    document.getElementById('description').value = filters.description;
  }
  document.getElementById('sortRadios' + filters.sort).checked = true;
  document.getElementById('price_min').value = filters.price_min;
  document.getElementById('price_max').value = filters.price_max;
}

function insertResultsInfo(count) {
  if (count) {
    var info = `Нашлось: ${count} объявлений.`
  } else {
    var info = 'Результатов нет.'
  }
  var container = document.getElementById("resultsInfo");
  container.innerHTML = info;
  container.className = "alert alert-info";
  container.role = "alert";

}

function text_truncate(str, length, ending) {
  if (length == null) {
    length = 100;
  }
  if (ending == null) {
    ending = '...';
  }
  if (str.length > length) {
    return str.substring(0, length - ending.length) + ending;
  } else {
    return str;
  }
};

function insertResults(elements) {
  function template(element) {
    var template = `
      <table class="table table-bordered"><tr><td>
        <a href="https://dom.ria.com/ru/${element.beautiful_url}">${element.title}</a>
        <br> район: ${element.district_name}
        <br> ${element.rooms_count} ком.
        | ${element.priceArr["3"]} грн.
        <br> ${text_truncate(element.description, 250)}
      </td></tr></table>
    `;
    return template;
  }
  insertElements(
    parentID='results',
    childClass='',
    elements=elements,
    templateFunc=template
  );
}

function insertPagination(page, pages, pagination) {
  var container = document.getElementById('pagination');
  container.innerHTML = "";
  if (!pagination.length){
    return;
  }

  if (page == 0){
    var template = `<button type="button" class="btn btn-outline-secondary" disabled><<</button>`;
  } else {
    var template = `<button type="button" class="btn btn-outline-secondary" onclick="gotoPage(${page - 1})"><<</button>`;
  }
  container.innerHTML += template;

  pagination.forEach(function(element) {
    if (element == '...'){
      var template = `<a href="#" class="btn btn-outline-secondary btn-lg disabled" tabindex="-1" role="button" aria-disabled="true"></a>`;
    } else {
      if (element - 1 == page){
        var template = `<button type="button" class="btn btn-primary" onclick="gotoPage(${element - 1})">${element}</button>`;
      } else{
        var template = `<button type="button" class="btn btn-outline-secondary" onclick="gotoPage(${element - 1})">${element}</button>`;
      }
    }
    container.innerHTML += template;
  })

  if (page + 1 == pages){
    var template = `<button type="button" class="btn btn-outline-secondary" disabled>>></button>`;
  } else {
    var template = `<button type="button" class="btn btn-outline-secondary" onclick="gotoPage(${page + 1})">>></button>`;
  }
  container.innerHTML += template;
}

function insertData(data) {
  // console.log(data);
  // console.log("insertData");
  setFilters(data.filters);
  insertResultsInfo(data.count);
  insertResults(data.results);
  insertPagination(data.page, data.pages, data.pagination);
}

function getData(query_string) {
  if (!query_string){
    var query_string = getQueryStringByFilters();
  }
  var APIBase = '/api/'
  var apiUrl = APIBase + query_string;

  console.log('getData: ' + apiUrl)
  document.getElementById('submitFilters').innerHTML = 'Оновлено!';
  setTimeout(function() {document.getElementById('submitFilters').innerHTML='';},1000);

  fetch(apiUrl)
   .then(function(response) {
    return response.json();
    })
   .then(function(data){
    insertData(data);
    window.history.pushState(data, '', query_string);
   })
   .catch(function(error) {
    console.log('fetch error: ' + error.message);
   });
}

function gotoPage(page) {
  var filters = window.history.state.filters;
  filters.page = page;
  var query_string = $.param(filters, true);
  getData("?" + query_string);
  document.getElementById('resultsInfo').scrollIntoView();
}

window.onload = function() {
  insertDistricts();
  insertRoomsCount();
  insertSorting();
  getData(window.location.search);
};
window.onpopstate = function(e){
  if(e.state){
    insertDistricts();
    insertRoomsCount();
    insertSorting();
    insertData(e.state);
  }
};
