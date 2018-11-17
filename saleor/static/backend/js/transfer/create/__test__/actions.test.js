
import { selectAcademicYear } from '../actions/academic-year'
import { addFeeItem, updateFeeItem, deleteFeeItem } from '../actions/action-fee-item'
import { setItems } from '../actions/action-items'
import { selectTerm } from '../actions/action-term'
import { selectCourse } from '../actions/course'

describe('[finance][fee]>>>A C T I O N --- Test select fee actions',()=>{
    it('sets payload for selected academic year ', () => {
        let action = selectAcademicYear({})
        expect(action).toEqual({type:"ACADEMIC_YEAR_SELECTED",payload:{}})
    });

    it('adds new fee item', () => {
        let action = addFeeItem({})
        expect(action).toEqual({type:"ADD_FEE_ITEM",payload:{}})
    });

    it('updates fee item', () => {
        let action = updateFeeItem({})
        expect(action).toEqual({type:"FEE_ITEM_UPDATED",payload:{}})
    });

    it('Delete fee item', () => {
        let action = deleteFeeItem(1)
        expect(action).toEqual({type:"FEE_ITEM_DELETED",Id:1})
    });

    it('Sets fee items', () => {
        let action = setItems({})
        expect(action).toEqual({type:"SET_ITEMS",payload:{}})
    });

    it('Sets terms', () => {
        let action = selectTerm({})
        expect(action).toEqual({type:"TERM_SELECTED",payload:{}})
    });

    it('Sets class (course) ', () => {
        let action = selectCourse({})
        expect(action).toEqual({type:"COURSE_SELECTED",payload:{}})
    });
});
//*******************************************************************************************************