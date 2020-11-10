var data = []
var token = ""

jQuery(document).ready(function() {
    document.getElementById('upload')
        .addEventListener('change', getFile)

    function getFile(event) {
        const input = event.target

        var filePath = input.value;
        var allowedExtensions = /(\.txt)$/i;

        if (!allowedExtensions.exec(filePath)) {
            alert('Invalid file type! Only .txt files are supported.');
        } else if ('files' in input && input.files.length > 0) {
            placeFileContent(
                document.getElementById('txt_input'),
                input.files[0])
        }
    }

    function placeFileContent(target, file) {
        readFileContent(file).then(content => {
            target.value = content
        }).catch(error => console.log(error))
    }

    function readFileContent(file) {
        const reader = new FileReader()
        return new Promise((resolve, reject) => {
            reader.onload = event => resolve(event.target.result)
            reader.onerror = error => reject(error)
            reader.readAsText(file)
        })
    }

    document.getElementById('download')
        .addEventListener('click', function() {
            var text = document.getElementById('input_summary').value;
            var filename = 'summary.txt';

            if (text !== '') {
                download(filename, text);
            }
        }, false)

    function download(filename, text) {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename);

        element.style.display = 'none';
        document.body.appendChild(element);

        element.click();
        document.body.removeChild(element);
    }

    var slider = $('#max_words')
    slider.on('change mousemove', function(evt) {
        $('#label_max_words').text(slider.val() + ' words')
    })

    var slider2 = $('#percentage')
    slider2.on('change mousemove', function(evt) {
        $('#label_percentage').text(slider2.val() + '%')
    })

    var slider3 = $('#num_beams')
    slider3.on('change mousemove', function(evt) {
        $('#label_num_beams').text('Beam search level: ' + slider3.val())
    })

    var slider4 = $('#ngram_size')
    slider4.on('change mousemove', function(evt) {
        $('#label_ngram_size').text('Non-repeating ngrams size: ' + slider4.val())
    })

    var slider5 = $('#max_buffer')
    slider5.on('change mousemove', function(evt) {
        $('#label_max_buffer').text('Max length buffer: ' + slider5.val())
    })

    var slider6 = $('#min_buffer')
    slider6.on('change mousemove', function(evt) {
        $('#label_min_buffer').text('Min length buffer: ' + slider6.val())
    })

    var option = $('#size')
    option.on('change', function(evt) {
        $("#" + $(this).val()).show().siblings().hide();
    })

    $('#btn-process').on('click', function() {
        input_text = $('#txt_input').val()

        if (option.val() == 'first') {
            num_words = $('#max_words').val()
            percentage = "0"
        } else {
            num_words = "0"
            percentage = $('#percentage').val()
        }

        num_beams = $('#num_beams').val()
        ngram_size = $('#ngram_size').val()
        max_buffer = $('#max_buffer').val()
        min_buffer = $('#min_buffer').val()
        repetition_penalty = $('#repetition_penalty').val()
        length_penalty = $('#length_penalty').val()

        $.ajax({
            url: '/generate',
            type: "post",
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({
                "input_text": input_text,
                "num_words": num_words,
                "percentage": percentage,
                "num_beams": num_beams,
                "no_repeat_ngram_size": ngram_size,
                "max_buffer": max_buffer,
                "min_buffer": min_buffer,
                "repetition_penalty": repetition_penalty,
                "length_penalty": length_penalty
            }),
            beforeSend: function() {
                $('#input_summary').val('Loading...')
            },
        }).done(function(jsondata, textStatus, jqXHR) {
            console.log(jsondata)
            $('#input_summary').val(jsondata['response']['summary'])
        }).fail(function(jsondata, textStatus, jqXHR) {
            alert(jsondata['responseJSON']['message'])
        });
    })
})