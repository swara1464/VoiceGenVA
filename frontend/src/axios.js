import axios from "axios";

axios.defaults.withCredentials = true;
axios.defaults.baseURL = "https://vocalagentapi.onrender.com";

export default axios;
