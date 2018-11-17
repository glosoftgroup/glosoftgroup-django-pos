import axios from 'axios';

class Api {

  static retrieve(url) {
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.xsrfCookieName = 'csrftoken';
    return axios.get(url)
    .then(response => {
      return response;
    }).catch(error => {
      throw error;
    });
  }

  static destroy(url) {
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.xsrfCookieName = 'csrftoken';
    return axios.delete(url)
    .then(response => {
      return response;
    }).catch(error => {
      throw error;
    });
  }

  static update(url, data) {
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.xsrfCookieName = 'csrftoken';
    return axios.put(url, data)
    .then(response => {
      return response;
    }).catch(error => {
      throw error;
    });
  }

  static create(url, data) {
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.xsrfCookieName = 'csrftoken';
    return axios.post(url, data)
    .then(response => {
      return response;
    }).catch(error => {
      throw error;
    });
  }
}

export default Api;
