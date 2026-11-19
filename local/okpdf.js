// okpdf: URL handler (Windows, per user). Opens a PDF from the Dropbox folder in a new Firefox tab.
// URL form: okpdf:<encodeURIComponent(path relative to %USERPROFILE%\Dropbox)>, e.g. okpdf:MIPT%2FAdam%2Fx.pdf
// Only existing .pdf files inside Dropbox are opened; anything else is ignored.
var sh=new ActiveXObject("WScript.Shell"), fso=new ActiveXObject("Scripting.FileSystemObject");
if(WScript.Arguments.length){
  var r=String(WScript.Arguments(0)).replace(/^okpdf:(\/\/)?/i,"").replace(/\/+$/,"");
  try{ r=decodeURIComponent(r); }catch(e){ r=""; }
  r=r.replace(/\//g,"\\");
  var ok=r && /\.pdf$/i.test(r) && ("\\"+r+"\\").indexOf("\\..\\")<0 && !/[:"*?<>|]/.test(r) && r.charAt(0)!="\\";
  var base=sh.ExpandEnvironmentStrings("%USERPROFILE%")+"\\Dropbox\\";
  if(ok && fso.FileExists(base+r)){
    // new tab in the running Firefox (its built-in PDF viewer); Okular was: %LOCALAPPDATA%\Microsoft\WindowsApps\okular.exe
    var u="file:///"+encodeURI((base+r).replace(/\\/g,"/")).replace(/#/g,"%23").replace(/\?/g,"%3F");
    sh.Run('"'+sh.ExpandEnvironmentStrings("%ProgramFiles%")+'\\Mozilla Firefox\\firefox.exe" -new-tab "'+u+'"',1,false);
  }
}
