<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>スタッフ用コンディション確認</title>

<style>
body{
  font-family:sans-serif;
  max-width:1100px;
  margin:auto;
  padding:20px;
}
h1{
  margin-bottom:20px;
}
.row{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin-bottom:20px;
}
input,button{
  padding:8px;
  font-size:16px;
}
button{
  cursor:pointer;
}
table{
  width:100%;
  border-collapse:collapse;
}
th,td{
  border:1px solid #ddd;
  padding:8px;
  text-align:center;
}
th{
  background:#f5f5f5;
}
.bad{
  color:#d60000;
  font-weight:bold;
}
.good{
  color:#008000;
}
.card{
  background:#f8f8f8;
  padding:12px;
  border-radius:10px;
}
</style>
</head>

<body>

<h1>スタッフ用コンディション確認</h1>

<div class="row">
  <div>
    開始日<br>
    <input type="date" id="startDate">
  </div>

  <div>
    終了日<br>
    <input type="date" id="endDate">
  </div>

  <div style="align-self:end;">
    <button onclick="loadData()">表示</button>
  </div>
</div>

<div id="status"></div>
<div id="result"></div>

<script>
const SUPABASE_URL = "https://zadmkthnxgbgsipxciuf.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InphZG1rdGhueGdiZ3NpcHhjaXVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM2NjMxNTEsImV4cCI6MjA1OTIzOTE1MX0.dv5vl3aZ6gcaDHi2-W3F4rT4wTrB3U1jgretX-yG_VU";

const STAFF_TEAM = "nigorigo"; // ←固定所属

function todayStr(){
 const d=new Date();
 return d.toISOString().split("T")[0];
}

document.getElementById("endDate").value=todayStr();

const before=new Date();
before.setDate(before.getDate()-7);
document.getElementById("startDate").value=before.toISOString().split("T")[0];

async function loadData(){

document.getElementById("status").innerHTML="読み込み中...";
document.getElementById("result").innerHTML="";

const start=document.getElementById("startDate").value;
const end=document.getElementById("endDate").value;

const url=
`${SUPABASE_URL}/rest/v1/condition?team=eq.${STAFF_TEAM}&date=gte.${start}&date=lte.${end}&order=date.asc`;

const res=await fetch(url,{
headers:{
apikey:SUPABASE_KEY,
Authorization:`Bearer ${SUPABASE_KEY}`
}
});

const data=await res.json();

if(!data || data.length===0){
document.getElementById("status").innerHTML="データなし";
return;
}

document.getElementById("status").innerHTML=
`${STAFF_TEAM} / ${data.length}件取得`;

const grouped={};

data.forEach(row=>{
if(!grouped[row.name]) grouped[row.name]=[];
grouped[row.name].push(row);
});

let html=`
<table>
<tr>
<th>名前</th>
<th>最新日</th>
<th>体調</th>
<th>疲労</th>
<th>睡眠</th>
<th>SpO₂</th>
<th>脈拍</th>
<th>コメント</th>
</tr>
`;

Object.keys(grouped).forEach(name=>{

const arr=grouped[name];
const latest=arr[arr.length-1];
const prev=arr.length>=2 ? arr[arr.length-2] : null;

let comment=[];

if(prev){

if(latest.health - prev.health <= -10){
comment.push("体調低下");
}

if(latest.fatigue - prev.fatigue >= 10){
comment.push("疲労増加");
}

if(latest.sleep_quality - prev.sleep_quality <= -10){
comment.push("睡眠低下");
}

if(latest.spo2 - prev.spo2 <= -2){
comment.push("SpO₂低下");
}

if(latest.pulse - prev.pulse >= 8){
comment.push("脈拍上昇");
}

if(latest.health - prev.health >= 10){
comment.push("体調改善");
}

if(latest.fatigue - prev.fatigue <= -10){
comment.push("疲労軽減");
}

}

if(comment.length===0){
comment.push("安定");
}

let cls="";

if(comment.includes("体調低下") ||
comment.includes("疲労増加") ||
comment.includes("SpO₂低下")){
cls="bad";
}

if(comment[0]==="安定"){
cls="good";
}

html+=`
<tr>
<td>${name}</td>
<td>${latest.date}</td>
<td>${latest.health}</td>
<td>${latest.fatigue}</td>
<td>${latest.sleep_quality}</td>
<td>${latest.spo2 ?? ""}</td>
<td>${latest.pulse ?? ""}</td>
<td class="${cls}">${comment.join(" / ")}</td>
</tr>
`;

});

html+="</table>";

document.getElementById("result").innerHTML=html;

}
</script>

</body>
</html>
