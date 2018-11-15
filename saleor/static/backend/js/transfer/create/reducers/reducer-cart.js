import { ADD_ITEM, DELETE_ITEM, UPDATE_ITEM } from '../actions/action-cart';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case ADD_ITEM:
      var add = true;
      state.map(item => {
        if (item.id === action.payload.id) {
          if (item.qty < item.quantity) {
            item.qty ++;
          }
          add = false;
          return;
        }
      });
      if (add) {
        action.payload.qty = 1;
        return [...state, action.payload];
      } else {
        return state;
      }
    case DELETE_ITEM:
      return state.filter(item => item.id !== action.itemId);
    case UPDATE_ITEM:
      return state.map(item => {
        if (item.id === action.payload.id) return action.payload;
        return item;
      });
    default:
      return state;
  }
};

// const incrementQty = (state, id) => {
//   return state.map(item => {
//     if (item.id === id) {
//       item.qty += 1;
//       return item;
//     }
//   });
// };
