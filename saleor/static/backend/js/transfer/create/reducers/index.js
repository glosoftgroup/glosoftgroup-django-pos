import { combineReducers } from 'redux';

import ItemReducer from './reducer-items';
import reducerCart from './reducer-cart';
import reducerSetCounter from './reducer-counter';
import ItemDate from './reducer-date';

const allReducers = combineReducers({
  items: ItemReducer,
  cart: reducerCart,
  counter: reducerSetCounter,
  date: ItemDate
});

function formatNumber(n, c, d, t) {
  c = isNaN(c = Math.abs(c)) ? 2 : c;
  d = d === undefined ? '.' : d;
  t = t === undefined ? ',' : t;
  var s = n < 0 ? '-' : '';
  var i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c)));
  var j = (j = i.length) > 3 ? j % 3 : 0;
  return s + (j ? i.substr(0, j) + t : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, '$1' + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : '');
};

export const getTotalQty = state => {
  var total = 0;
  state.cart.map((value, index) => {
    if (value.qty) {
      total += parseInt(value.qty);
    }
  });
  return total;
};

export const getTotalWorth = state => {
  var total = 0;
  state.cart.map((value, index) => {
    if (value.qty) {
      total += parseInt(value.qty) * value.cost_price;
    }
  });
  return formatNumber(total, 2, '.', ',');
};

export const cartValidation = state => {
  /* return false if one of the cart item quantity is not set */
  var validity = true;
  state.cart.map((value, index) => {
    console.log(value);
    if (!value.qty) {
      validity = false;
    }
  });
  return validity;
};

export default allReducers;
