export const ADD_ITEM = 'ADD_ITEM';
export const DELETE_ITEM = 'DELETE_ITEM';
export const UPDATE_ITEM = 'UPDATE_ITEM';

export const addCartItem = (payload) => ({
  type: ADD_ITEM,
  payload
});

export const updateCartItem = (payload) => ({
  type: UPDATE_ITEM,
  payload
});

export const deleteCartItem = (itemId) => ({
  type: DELETE_ITEM,
  itemId
});
