
$(document).ready(function() {

    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

});
var i =0;
var info=[];
var csvFilesFound = [];
function showDicomFiles(context)
{
    var filesList = document.getElementById( 'client-files' ).files;
    if( Array.from(filesList).length == 0 )
        return;
    csvFilesFound = [];
    info = [];
    i = 0;
    // retrieve files from the input type=file 
        //empty all the files within the image container
    document.getElementById("imagesContainer").innerHTML = "";
    // Add our tool, and set it's mode
    cornerstoneWADOImageLoader.wadouri.fileManager.purge();


    Array.from(filesList).forEach( function( file ){
        fileName = file.name;
        if( validFile( file ) )
        {
            document.getElementById("imagesContainer").insertAdjacentHTML('beforeend',  generateHTMLContentForImage(filesList[i]) );         
            element  = $("div[id='" + fileName + "_img_holder']").get(0);
            fileNameElement  = $("div[id='" + fileName + "_img_name']").get(0);
            fileNameElement.innerHTML = fileName;
            cornerstone.enable(element);
            imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
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

    Array.from(info).forEach( function( info ) {
    var element = cornerstone.loadImage(info[1]).then(function(image) {
        cornerstone.displayImage(info[0], image);
        cornerstoneTools.mouseInput.enable(info[0]);
        cornerstoneTools.mouseWheelInput.enable(info[0]);
        cornerstoneTools.wwwc.activate(info[0], 1); // ww/wc is the default tool for left mouse button
        cornerstoneTools.pan.activate(info[0], 2); // pan is the default tool for middle mouse button
        cornerstoneTools.zoom.activate(info[0], 4); // zoom is the default tool for right mouse button
        cornerstoneTools.zoomWheel.activate(info[0]); // zoom is the default tool for middle mouse wheel

    });
    });
    
    
    updateAnnotationFileFound();
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
    '<div id=\"' + fileName + "_img_holder" + '\" style="width:100%;height:94%;top:0px;left:0px; position:absolute">',
    '</div>',
    '<div id=\"' + fileName + "_img_name" + '\" style="position:absolute;top:0px;left:0px;color:white">',
    '</div>',
    '<div style="top:330px;width:100%; position:absolute; display:inline;color:black;margin:0px;">',
    '<input  checked type="radio"  name=\"' + fileName + '\" value="low" />',
        '<label for="one">Low</label>',
        '<input  type="radio" style="margin-left:25%" name=\"' + fileName + '\" value="medium" />',
        '<label for="two">Medium</label>',
        '<input onchange="myFunction()" type="radio"  style=\"margin-left:17%\"name=\"' + fileName + '\" value="high" />',
        '<label for="two">High</label>',
    '</div>',
'</div >' 
].join("\n");

   // console.log( htmlString );
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
  document.getElementById( "folderLoc"  ).value = document.getElementById( "folder_loc"  ).value;
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
    var csvContent = getContent( document.getElementById("folderLoc").value );
    var fileName = document.getElementById("annotationFileName").value;
    if( fileName.length == 0 )
        {
            alert("Please provide annotation File Name");
            return;
        }

    download(fileName, csvContent);
    document.getElementById("retrieveAnnotation").style.display="none";
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