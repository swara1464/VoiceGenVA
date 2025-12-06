import axios from "axios";

axios.defaults.withCredentials = false;
axios.defaults.baseURL = "https://vocalagentapi.onrender.com";

export default axios;
