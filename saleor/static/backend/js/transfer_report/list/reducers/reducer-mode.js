import { SET_MODE } from '../actions/action-mode.js';

export default function (state = null, action) {
  switch (action.type) {
    case SET_MODE:
      return action.payload;
  }
  return state;
};
