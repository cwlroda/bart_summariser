var data = []
var token = ""
var documents = []
var summaries = []

jQuery(document).ready(function() {
    document.getElementById('upload')
        .addEventListener('change', getFile)

    function getFile(event) {
        document.getElementById('txt_input').value = ''
        var input = event.target

        if (input.files.length == 1) {
            var filePath = input.value;
            var allowedExtensions = /(\.txt)$/i;

            if (!allowedExtensions.exec(filePath)) {
                alert('Invalid file type! Only .txt files are supported.');
            } else {
                placeFileContent(
                    document.getElementById('txt_input'),
                    input.files[0])
            }
        } else {
            for (var i = 0; i < input.files.length; i++) {
                var filePath = input.files[i].name;
                var allowedExtensions = /(\.txt)$/i;

                if (!allowedExtensions.exec(filePath)) {
                    alert('Invalid file type! Only .txt files are supported.');
                } else {
                    document.getElementById('txt_input').value += input.files[i].name + '\n';
                    appendFileContent(
                        documents,
                        input.files[i])
                }
            }
        }
    }

    function appendFileContent(target, file) {
        readFileContent(file).then(content => {
            target.push(content)
            $('#label_files').text(documents.length + ' file(s) uploaded')
        }).catch(error => console.log(error))
    }

    function placeFileContent(target, file) {
        readFileContent(file).then(content => {
            target.value = content
            $('#label_files').text('1 file(s) uploaded')
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
            if (summaries.length) {
                for (var i = 1; i < summaries.length + 1; i++) {
                    var filename = 'summary' + i + '.txt';

                    if (summaries[i - 1] !== '') {
                        download(filename, summaries[i - 1]);
                    }
                }
            } else {
                var text = document.getElementById('input_summary').value;
                var filename = 'summary.txt';

                if (text !== '') {
                    download(filename, text);
                }
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
        if (documents.length) {
            input_text = ""
        } else {
            input_text = $('#txt_input').val()
        }

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
                "documents": documents,
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
                $('#label_files').text('')
                summaries = []
            },
        }).done(function(jsondata, textStatus, jqXHR) {
            console.log(jsondata)

            if (jsondata['response']['documents'].length) {
                summaries = jsondata['response']['documents']
                $('#input_summary').val('Generated ' + summaries.length + '/' + documents.length + ' summaries')
            } else {
                $('#input_summary').val(jsondata['response']['summary'])
            }

            documents = []
        }).fail(function(jsondata, textStatus, jqXHR) {
            alert(jsondata['responseJSON']['message'])
        });
    })
})