
$(document).ready(function() {

   
});
var i =0;
var info=[];
var csvFilesFound = [];
function showDicomFiles(context)
{
    console.log( context );
    csvFilesFound = [];
    info = [];
    i = 0;
    // retrieve files from the input type=file 
    var filesList = document.getElementById( 'client-files' ).files;
    cornerstoneFileImageLoader.purge();
    //empty all the files within the image container
    document.getElementById("imagesContainer").innerHTML = "";
    // Add our tool, and set it's mode


    Array.from(filesList).forEach( function( file ){
        fileName = file.name;
        if( validFile( file ) )
        {
            document.getElementById("imagesContainer").insertAdjacentHTML('beforeend',  generateHTMLContentForImage(filesList[i]) );         
            element  = $("div[id='" + fileName + "_img_holder']").get(0);
            cornerstone.enable(element);
            var index = cornerstoneFileImageLoader.addFile(file);
            // create an imageId for this image
            imageId = "dicomfile://" + index;
            info[i] = new Array(2);
            info[i][0] =  element;
            info[i][1] = imageId;
            i++;
            var context = this;     
        }
        else if ( fileName.endsWith( ".csv" ) )
        {
            csvFilesFound.push( fileName );
        }

    });
    cornerstoneTools.init();
    cornerstoneTools.external.cornerstone = cornerstone;
    cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
    cornerstoneTools.setToolActive();
    Array.from(info).forEach( function( info ) {
    var element = cornerstone.loadImage(info[1]).then(function(image) {
        console.log(  info[0] );
        cornerstone.displayImage(info[0], image);
        cornerstoneTools.mouseInput.enable(info[0]);
        cornerstoneTools.mouseWheelInput.enable(info[0]);
        // cornerstoneTools.wwwc.activate(info[0], 1); // Left Click
        // cornerstoneTools.pan.activate(info[0], 2); // Middle Click
        // cornerstoneTools.zoom.activate(info[0], 4); // Right Click
        // cornerstoneTools.zoomWheel.activate(info[0]); // Mouse Wheel
    });
    });

    updateAnnotationFileFound();

    console.log( filesList );
    attachRadioButtonEvent();
}
function updateAnnotationFileFound()
{
    annotationLabel = document.getElementById( "annotationLabel"  );
    annotationFiles = document.getElementById( "annotationFiles"  );
    if( csvFilesFound.length ==  0 )
    {
        annotationLabel.style.display = "none";
        annotationFiles.style.display = "none";
    
    return;
    }
    annotationLabel.style.display = "inline";
    annotationFiles.style.display = "inline";
    annotationFiles.innerHTML = csvFilesFound.toString();
    
}
function attachRadioButtonEvent()
{
    $('input[type=radio]').on('change', function() {
        switch ($(this).val()) {
        case 'low':
        $(this).parent().parent()[0].style.borderColor="white";
          break;
        case 'medium':
        $(this).parent().parent()[0].style.borderColor="blue";
          break;
          case 'high':
          $(this).parent().parent()[0].style.borderColor="yellow";
          break;
        }

    // Listen for the change event on our input element so we can get the
    // file selected by the user
    });
}

function generateHTMLContentForImage( fileInfo )
{
    var fileName = fileInfo.name;
    var htmlString = [ '<div class = "image" >',
    '<div id=\"' + fileName + "_img_holder" + '\" style="width:330px;height:330px;top:0px;left:0px; position:absolute">',
    '</div>',
    '<div style="top:330px;width:375px; position:absolute; display:inline;color:black;margin:0px;">',
    '<input  checked type="radio"  name=\"' + fileName + '\" value="low" />',
        '<label for="one">Low</label>',
        '<input  type="radio" style="margin-left:18%" name=\"' + fileName + '\" value="medium" />',
        '<label for="two">Medium</label>',
        '<input onchange="myFunction()" type="radio"  style=\"margin-left:18%\"name=\"' + fileName + '\" value="high" />',
        '<label for="two">High</label>',
    '</div>',
'</div >' 
].join("\n");

    console.log( htmlString );
    return htmlString;

}

function validFile( fileInfo  )
{
    return fileInfo.name.endsWith( ".dcm" );
}

function getParentDirectory(){
    var folderPath = document.getElementById( 'folder-url' ).value;

    if( typeof(folderPath) == 'undefined' || folderPath === null || folderPath == ""   )
        alert( 'Please provide valid folder folder path containig DICOM Images ');
    return folderPath;
}

// Get the modal
var modal = document.getElementById("retrieveAnnotation");

// Get the button that opens the modal
var btn = document.getElementById("retrieveAnnotationBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
function retrieveAnnotation()
{
    
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href',  "data:text/csv;charset=utf-8," + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

// Start file download.
document.getElementById("download").addEventListener("click", function(){
    // Generate download of hello.txt file with some content
    var csvContent = getContent( document.getElementById("folderLoc").value );
    var fileName = document.getElementById("annotationFileName").value;
    
    
    download(fileName, csvContent);
}, false);

function getContent( folderPath )
{
    radioBoxes = $('input[type=radio]:checked');
    content  = "";
    Array.from(radioBoxes).forEach( function( radioBox ){
        row = folderPath + "\\" + radioBox.name + "," + radioBox.value + "\r\n";
        content = content + row;
    });
    console.log( content );
    return content;
}