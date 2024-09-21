const searchForm = document.getElementById('search-form')
const searchContainer = document.getElementById('search-container')
const baseEndpoint = "http://localhost:8000/api"

if (searchForm){
    searchForm.addEventListener('submit', handleSearch)
}

function handleSearch(event){
    event.preventDefault()
    
    let formData = new FormData(searchForm)
    let data = Object.fromEntries(formData)
    let searhParams = new URLSearchParams(data)
    const endpoint = `${baseEndpoint}/search/?${searhParams}`
    const options = {
        method: 'GET',
        headers:{
            "Content-Type": "application/json",
        }
    }
    fetch(endpoint, options)
    .then(response=>{
        return response.json()
    })
    .then(data=> {
        writeToContainer(data)
    })
    .catch(err => {
        console.log(err)
    })
}

function writeToContainer(data){
    const dataObj = JSON.parse(JSON.stringify(data));
    if (searchContainer){
        searchContainer.innerHTML = 
        "<div>"+
        "<img src='media/"+dataObj.hits[0].image+"' alt='product image'>"+
        "</div>"+
        "<div class='p-4'>"+
        "<span class='font-bold text-gray-500 text-sm'>"+dataObj.hits[0].title+"</span>"+
        "</div>"+
        "<div>"+
        "<span class='font-bold text-gray-500 text-sm'> Quantity: "+dataObj.hits[0].quantity+"</span>"
        "</div>"+
        "<pre>" + 
        JSON.stringify(data, null, 4) + 
        "</pre>"
    }
}