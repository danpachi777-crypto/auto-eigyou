import {readFile,writeFile,mkdir,cp} from 'node:fs/promises';
import {resolve} from 'node:path';
const root=resolve(import.meta.dirname,'..');
const source=await readFile(resolve(root,'worker/index.js'),'utf8');
const files={HOME_HTML:'index.html',RESERVE_HTML:'reserve.html',ADMIN_HTML:'admin.html',STYLES:'styles.css',FORMS_CSS:'forms.css',RESERVE_JS:'reserve.js',ADMIN_JS:'admin.js'};
let output=source;
for(const [key,file] of Object.entries(files)){const content=await readFile(resolve(root,'web',file),'utf8');output=output.replace(`"__${key}__"`,JSON.stringify(content));}
await mkdir(resolve(root,'dist/server'),{recursive:true});
await mkdir(resolve(root,'dist/.openai'),{recursive:true});
await writeFile(resolve(root,'dist/server/index.js'),output);
await cp(resolve(root,'.openai/hosting.json'),resolve(root,'dist/.openai/hosting.json'));
await cp(resolve(root,'drizzle'),resolve(root,'dist/.openai/drizzle'),{recursive:true,force:true});
console.log('Built Worker and reservation migration');
