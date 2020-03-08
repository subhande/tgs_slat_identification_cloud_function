var imagePreview = document.querySelector('#image-preview');
var imageResult = document.querySelector('#image-result');
var input = document.querySelector('#imageUpload');
var button = document.querySelector("#result-button");
var loader = document.querySelector('.loader-container');
button.disabled = true;
input.addEventListener('change', function (event) {
    imagePreview.src = URL.createObjectURL(event.target.files[0]);
    imagePreview.style.visibility = "visible";
    button.disabled = false;
})


// This funtion sends input to server and in response it receives predicted image

const sendFile = () => {
    loader.style.display = "block";
    button.disabled = true;
    var data = new FormData()
    if(!input.files[0])
        return;
    // data.append("file", input.files[0])

    var file = input.files[0];
    var reader = new FileReader();
    reader.onloadend = function() {
        
        // console.log(JSON.stringify({"image" : reader.result}))
        fetch('https://us-central1-flask-app-268504.cloudfunctions.net/echo', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({"image": reader.result}),
        }).then((response) => {
            return response.json();
        })
        .then((myJson) => {
            // console.log(myJson);
            loader.style.display = "none";
            var b64 =  myJson['image'].split("'")[1];
            // console.log(myJson['image'])
            imageResult.src = 'data:image/png;base64,' + b64;
            imageResult.style.visibility = "visible";
            button.disabled = false;
        })
        .catch((error) => {
            console.error('Error:', error);
          });


    }
    reader.readAsDataURL(file);
    // console.log(JSON.stringify({"image" : reader.result}))


    // fetch('/predict', {
    // method: 'POST',
    // headers: {
    //     'Content-Type': 'application/json',
    // },
    // body: JSON.stringify({"image": reader})
    // }).then((response) => {
    //     return response.json();
    //   })
    //   .then((myJson) => {
    //     var b64 =  myJson['image'].split("'")[1];
    //     imageResult.src = 'data:image/png;base64,' + b64;
    //     imageResult.style.visibility = "visible";
    //   });
}

function activeUpload() {
    input.click();
}