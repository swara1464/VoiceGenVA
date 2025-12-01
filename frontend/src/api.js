/*const BASE_URL = "http://localhost:5000"; // Flask running here*/
const BASE_URL = "http://127.0.0.1:5050";

export async function echoTest(message) {
  const res = await fetch(`${BASE_URL}/echo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  return res.json();
}

export async function checkLogin() {
  const res = await fetch(`${BASE_URL}/auth/check`, {
    credentials: "include",
  });
  return res.json();
}
