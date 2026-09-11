
const definitions = {
  1:{title:"Image Representation & Operations",aim:"Convert RGB and grayscale images and study arithmetic and bitwise operations.", controls:`
    <div class="control-grid"><div class="field"><label>Operation</label><select name="operation" id="op">
      <option value="grayscale">RGB → Grayscale</option><option value="rgb">RGB Image</option><option value="add">Image Addition</option><option value="subtract">Image Subtraction</option><option value="and">Bitwise AND</option><option value="or">Bitwise OR</option><option value="xor">Bitwise XOR</option>
    </select></div><div class="field" id="valueField"><label>Pixel value / mask</label><input type="number" name="value" value="40" min="0" max="255"></div></div>`},
  2:{title:"2-D Geometric Transformations",aim:"Apply Translation, Rotation, Scaling, Shearing, Reflection and Cropping to an image.", controls:`
    <div class="control-grid"><div class="field"><label>Transformation</label><select name="operation" id="op"><option value="translation">Translation</option><option value="rotation">Rotation</option><option value="scaling">Scaling</option><option value="shearing">Shearing</option><option value="reflection">Reflection</option><option value="cropping">Cropping</option></select></div><div class="field" id="dynamicFields"></div></div>`},
  3:{title:"Spatial Domain Enhancement",aim:"Improve contrast, smooth images, sharpen important features and segment grayscale images.", controls:`
    <div class="control-grid"><div class="field"><label>Technique</label><select name="operation" id="op"><option value="histogram">Histogram Equalization</option><option value="smoothing">Smoothing</option><option value="sharpening">Sharpening</option><option value="threshold">Thresholding</option></select></div><div class="field" id="dynamicFields"></div></div>`},
  4:{title:"Spatial Domain Filters",aim:"Apply Averaging, Gaussian, Median and Bilateral filters and observe their effect on noise.", controls:`
    <div class="control-grid"><div class="field"><label>Filter</label><select name="operation"><option value="average">Averaging Filter</option><option value="gaussian">Gaussian Filter</option><option value="median">Median Filter</option><option value="bilateral">Bilateral Filter</option></select></div><div class="field"><label>Kernel size</label><select name="kernel"><option>3</option><option selected>5</option><option>7</option><option>9</option><option>11</option></select></div></div>`},
  5:{title:"Image Inpainting",aim:"Restore damaged image regions using Telea and Navier–Stokes methods.", controls:`
    <div class="control-grid"><div class="field"><label>Inpainting method</label><select name="operation"><option value="telea">Telea Method</option><option value="ns">Navier–Stokes (NS) Method</option></select></div></div>`},
  6:{title:"Lossless Compression",aim:"Implement a coding technique for lossless compression and compare original and compressed representations.", controls:`
    <div class="control-grid"><div class="field"><label>Coding technique</label><select name="operation"><option value="huffman">Huffman Coding</option></select></div></div>`},
  7:{title:"Morphological Operations",aim:"Study Erosion, Dilation, Opening and Closing on binary images.", controls:`
    <div class="control-grid"><div class="field"><label>Operation</label><select name="operation"><option value="erosion">Erosion</option><option value="dilation">Dilation</option><option value="opening">Opening</option><option value="closing">Closing</option></select></div><div class="field"><label>Kernel size</label><select name="kernel"><option>3</option><option selected>5</option><option>7</option><option>9</option></select></div><div class="field"><label>Threshold</label><input type="number" name="threshold" value="127" min="0" max="255"></div></div>`},
  8:{title:"Correlation-Based Object Detection",aim:"Detect an object by comparing a template with regions of the input image using correlation.", controls:`
    <div class="control-grid"><div class="field"><label>Matching principle</label><select name="operation"><option value="correlation">Normalized Correlation / Template Matching</option></select></div></div>`},
  9:{title:"Colour Space Conversion",aim:"Convert between RGB, HSV, YCrCb and Lab and study how colour information is encoded.", controls:`
    <div class="control-grid"><div class="field"><label>Colour space</label><select name="operation"><option value="rgb">RGB</option><option value="hsv">HSV</option><option value="ycrcb">YCrCb</option><option value="lab">Lab</option></select></div></div>`},
  10:{title:"Edge Detection",aim:"Detect and compare image edges using Canny, Sobel and Prewitt detectors.", controls:`
    <div class="control-grid"><div class="field"><label>Detector</label><select name="operation" id="op"><option value="canny">Canny</option><option value="sobel">Sobel</option><option value="prewitt">Prewitt</option></select></div><div class="field" id="dynamicFields"></div></div>`}
};

const form=document.getElementById("form"), controls=document.getElementById("controls"), extra=document.getElementById("extraUpload");
const practical=document.getElementById("practical"), fileInput=document.getElementById("image"), filename=document.getElementById("filename");
let latestOutputUrl="";

function field(label,name,value,min,max,step="1"){return `<label>${label}</label><div class="range-line"><input type="range" name="${name}" value="${value}" min="${min}" max="${max}" step="${step}" oninput="this.nextElementSibling.textContent=this.value"><span class="range-value">${value}</span></div>`}
function updateDynamic(){
  const p=practical.value, op=document.getElementById("op"), dyn=document.getElementById("dynamicFields");
  if(!dyn)return;
  if(p==="2"){
    if(op.value==="translation") dyn.innerHTML=`${field("X shift","tx",50,-300,300)}<br>${field("Y shift","ty",30,-300,300)}`;
    else if(op.value==="rotation") dyn.innerHTML=field("Angle (degrees)","angle",30,-180,180);
    else if(op.value==="scaling") dyn.innerHTML=field("Scale","scale",1.3,.1,3,.1);
    else if(op.value==="shearing") dyn.innerHTML=`${field("X shear","shx",0.2,-1,1,.05)}<br>${field("Y shear","shy",0,-1,1,.05)}`;
    else if(op.value==="reflection") dyn.innerHTML=`<label>Axis</label><select name="axis"><option value="horizontal">Horizontal axis</option><option value="vertical">Vertical axis</option></select>`;
    else dyn.innerHTML=`<div class="control-grid"><div class="field"><label>X</label><input type="number" name="x" value="10"></div><div class="field"><label>Y</label><input type="number" name="y" value="10"></div><div class="field"><label>Width</label><input type="number" name="cw" value="300"></div><div class="field"><label>Height</label><input type="number" name="ch" value="300"></div></div>`;
  } else if(p==="3"){
    if(op.value==="smoothing") dyn.innerHTML=`<label>Kernel</label><select name="kernel"><option>3</option><option selected>5</option><option>7</option><option>9</option></select>`;
    else if(op.value==="threshold") dyn.innerHTML=field("Threshold","threshold",127,0,255);
    else dyn.innerHTML="";
  } else if(p==="10"){
    if(op.value==="canny") dyn.innerHTML=`${field("Low threshold","low",50,0,255)}<br>${field("High threshold","high",150,1,255)}`;
    else dyn.innerHTML="";
  }
  document.querySelectorAll("#op").forEach(x=>x.onchange=updateDynamic);
}
function updateExtra(){
  if(practical.value==="5") extra.innerHTML=`<div class="extra"><div class="extra-title">03 • Damage mask</div><div class="field"><label>Mask image — white = damaged, black = preserved</label><input type="file" name="mask" accept="image/*"></div></div>`;
  else if(practical.value==="8") extra.innerHTML=`<div class="extra"><div class="extra-title">03 • Template image</div><div class="field"><label>Upload a smaller template containing the object to detect</label><input type="file" name="template" accept="image/*"></div></div>`;
  else extra.innerHTML="";
}
function loadPractical(p){
  const d=definitions[p]; practical.value=p; document.getElementById("pTag").textContent=`PRACTICAL ${String(p).padStart(2,"0")}`;
  document.getElementById("pTitle").textContent=d.title; document.getElementById("pAim").textContent=d.aim; controls.innerHTML=d.controls; updateExtra(); updateDynamic();
  document.querySelectorAll(".pbtn").forEach(b=>b.classList.toggle("active",b.dataset.p===String(p)));
}
document.querySelectorAll(".pbtn").forEach(b=>b.addEventListener("click",()=>loadPractical(b.dataset.p)));
fileInput.addEventListener("change",()=>{filename.textContent=fileInput.files[0]?.name||""; if(fileInput.files[0]){const r=new FileReader();r.onload=e=>document.getElementById("inputPreview").innerHTML=`<img src="${e.target.result}" alt="Input image preview">`;r.readAsDataURL(fileInput.files[0])}});

form.addEventListener("submit",async e=>{
  e.preventDefault();
  const btn=document.querySelector(".run"); btn.disabled=true; btn.querySelector("span").textContent="Processing…";
  try{
    const res=await fetch("/api/process",{method:"POST",body:new FormData(form)}), data=await res.json();
    if(!data.ok) throw new Error(data.error);
    document.getElementById("resultTitle").textContent=data.title;
    document.getElementById("outputPreview").innerHTML=`<img src="${data.image}" alt="Processed output preview">`;
    latestOutputUrl=data.image; const openOutput=document.getElementById("openOutput"); const downloadOutput=document.getElementById("downloadOutput"); openOutput.disabled=false; downloadOutput.href=data.image; downloadOutput.classList.remove("disabled-link");
    document.getElementById("inStats").textContent=`${data.input_stats.width}×${data.input_stats.height} • ${data.input_stats.channels} channel(s) • mean ${data.input_stats.mean}`;
    document.getElementById("outStats").textContent=`${data.output_stats.width}×${data.output_stats.height} • ${data.output_stats.channels} channel(s) • mean ${data.output_stats.mean}`;
    document.getElementById("note").textContent=data.note||"Processing completed successfully.";
    const m=data.metric||{}; let badge="";
    if(m.correlation_score!==undefined) badge=`Correlation ${m.correlation_score}`;
    else if(m.compression_ratio) badge=`Huffman ratio ${m.compression_ratio}:1`;
    else if(m.space_saving!==undefined) badge=`${m.space_saving}% bit saving`;
    document.getElementById("metricBadge").innerHTML=badge?`<div class="metric">${badge}</div>`:"";
  }catch(err){alert(err.message)}finally{btn.disabled=false;btn.querySelector("span").textContent="Run Processing"}
});
loadPractical("1");


const imageModal=document.getElementById("imageModal");
const modalImage=document.getElementById("modalImage");
const modalTitle=document.getElementById("modalTitle");
function openImageModal(src,title){ if(!src) return; modalImage.src=src; modalTitle.textContent=title||"Image Preview"; imageModal.classList.add("open"); imageModal.setAttribute("aria-hidden","false"); document.body.style.overflow="hidden"; }
function closeImageModal(){ imageModal.classList.remove("open"); imageModal.setAttribute("aria-hidden","true"); modalImage.src=""; document.body.style.overflow=""; }
document.addEventListener("click",e=>{ const view=e.target.closest(".view-btn"); if(view){ const holder=document.getElementById(view.dataset.view); const img=holder?.querySelector("img"); if(img) openImageModal(img.src, view.dataset.view==="inputPreview"?"Input Image":"Processed Output"); } const img=e.target.closest(".image-box img"); if(img) openImageModal(img.src, img.alt||"Image Preview"); if(e.target.closest("[data-close-modal]")) closeImageModal(); });
document.getElementById("openOutput").addEventListener("click",()=>openImageModal(latestOutputUrl,"Processed Output"));
document.addEventListener("keydown",e=>{if(e.key==="Escape") closeImageModal();});
