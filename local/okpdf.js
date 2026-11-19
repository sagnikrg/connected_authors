// okpdf: URL handler (Windows, per user). Opens a PDF from the Dropbox folder in Okular.
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
    sh.Run('"'+sh.ExpandEnvironmentStrings("%LOCALAPPDATA%")+'\\Microsoft\\WindowsApps\\okular.exe" "'+base+r+'"',1,false);
  }
}
