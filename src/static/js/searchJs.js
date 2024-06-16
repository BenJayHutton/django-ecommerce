async function searchProduct() {
    let myPromise = new Promise(function(resolve, reject) {
      resolve("I love You !!");
    });
    document.getElementById("search_results").innerHTML = await myPromise;
  }

  searchProduct();