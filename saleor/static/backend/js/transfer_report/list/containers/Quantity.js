import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import Tooltip from 'react-tooltip-lite';
import api from '../api/Api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export class Quantity extends Component {
  constructor(props) {
    super(props);
    this.state = {
      qty: 1,
      maxQty: 0,
      isOpen: false,
      edit: false
    };
  }

  componentDidMount = () => {
    this.setState({
      qty: this.props.instance.qty,
      maxQty: this.props.instance.quantity
    });
  }
  isNumeric = (n) => {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }

  handleChange = (e) => {
    // transfer qty should not exceed store qty
    var value = e.target.value;

    if (!this.isNumeric(value)) {
      toast.error('Quantity must be a digit!');
      return;
    }
    if (value < 1) {
      toast.error('Quantity must more than one!');
      return;
    }
    if (value > this.state.maxQty) {
      toast.error('Transfer Quantity cannot be more than ' + this.state.maxQty + '!');
      return;
    } else {
      this.setState({
        [e.target.name]: value
      });
      var payload = Object.assign(this.props.instance);
      payload.qty = value;
    }
  }

  handleSubmit = () => {
    var formData = new FormData();
    formData.append('qty', this.props.instance.qty);
    formData.append('price', (this.props.instance.unit_price * this.props.instance.qty));
    api.update('/counter/transfer/api/update/item/' + this.props.instance.id + '/', formData)
    .then((response) => {
      this.setState({isOpen: false});
    })
    .catch((error) => { console.log(error); });
  }

  toggleEdit = () => {
    this.setState({isOpen: !this.state.isOpen});
  }

  render() {
    return (
      <div className="row">
        <ToastContainer />
        <ReactTooltip place="bottom"/>
        <div onClick={this.toggleEdit} className="col-md-8">
          {!this.state.edit &&
          <Tooltip isOpen={this.state.isOpen} content={(
            <div>
              <div className="editableform" >
                <div className="control-group form-group">
                  <div className="editable-input">
                    <input value={this.props.instance.qty} onChange={this.handleChange}
                    type="number" name="quantity" className="form-control"
                    />
                  </div>
                  <div className="editable-buttons">
                    <button onClick={this.handleSubmit} type="submit" className="btn btn-primary btn-icon editable-submit">
                      <i className="icon-check"></i>
                    </button>
                    <button onClick={this.toggleEdit} type="button" className="btn btn-default btn-icon editable-cancel">
                      <i className="icon-x"></i>
                    </button>
                  </div>
                  <div className="editable-error-block help-block hidden"></div>
                </div>
              </div>
            </div>
          )}
            className="target" tagName="span" eventToggle="onClick">
            <span data-tip="Edit quantity" className="edit-qty text-primary cursor-pointer">
              {this.props.instance.qty}
            </span>
        </Tooltip>
          }
        </div>
        <div className="col-md-4 mt-5">
        {this.state.edit &&
         <span onClick={this.editInstance} className="animated zoomIn btn btn-sm btn-primary cursor-pointer">Save</span>
        }
        </div>
      </div>
    );
  }
}

Quantity.propTypes = {
  instance: PropTypes.array.isRequired,
  updateCartItem: PropTypes.func.isRequired
};

function mapStateToProps(state) {
  return {};
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}

export default connect(mapStateToProps, matchDispatchToProps)(Quantity);
