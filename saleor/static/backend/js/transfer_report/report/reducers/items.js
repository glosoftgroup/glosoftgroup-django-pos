import { SET_ITEMS } from '../actions/items';

const initialState = {
  'links': {
    'next': null,
    'previous': null
  },
  'count': 7,
  'total_pages': 1,
  'results': []
};

export default (state = initialState, action) => {
  switch (action.type) {
    case SET_ITEMS:
      return action.payload;
    default:
      return state;
  }
};
