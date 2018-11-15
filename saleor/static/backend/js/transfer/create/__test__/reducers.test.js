import React from 'react'
import { shallow, mount } from 'enzyme';
// import renderer from 'react-test-renderer'
import { COURSE_SELECTED } from '../actions/course.js';
import { DATE_SELECTED } from '../actions/date.js';
import { ACADEMIC_YEAR_SELECTED } from '../actions/academic-year.js';
import { ADD_FEE_ITEM, FEE_ITEM_UPDATED, FEE_ITEM_DELETED } from '../actions/action-fee-item'
import { SET_STRUCTURE, ADD_STRUCTURE, STRUCTURE_DELETED } from '../actions/action-fee-structure';

import courseReducer from '../reducers/reducer-active-course'
import termReducer from '../reducers/reducer-active-term'
import yearReducer from '../reducers/reducer-active-year'
import ItemsReducer from '../reducers/reducer-fee-items'

describe('[Finance][fee]>>>R E D U C E R --- Test finance [fee structure] reducer',()=>{
    it('+++ reducer for COURSE_SELECTED', () => {
        let state = {type: COURSE_SELECTED, payload:{id:12}}
        state = courseReducer({}, state)
        expect(state).toEqual({id:12})
    });

    it('+++ reducer for TERM_SELECTED', () => {
        let state = {type: TERM_SELECTED, payload:{id:12}}
        state = termReducer({}, state)
        expect(state).toEqual({id:12})
    });

    it('+++ reducer for ACADEMIC_YEAR_SELECTED', () => {
        let state = {type: ACADEMIC_YEAR_SELECTED, payload:{id:13}}
        state = termReducer({}, state)
        expect(state).toEqual({})
    });

    it('+++ reducer for ADD_FEE_ITEM', () => {
        let state = {type: ADD_FEE_ITEM, payload:{id:12}}
        state = ItemsReducer([], state)
        expect(state).toEqual([{id:12}])
    });

    it('+++ reducer for ADD_FEE_ITEM', () => {
        let state = {type: FEE_ITEM_DELETED, payload:{id:12}}
        state = ItemsReducer([], state)
        expect(state).toEqual([{id:12}])
    });

});
//*******************************************************************************************************