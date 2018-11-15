import React from 'react';
import { Modal, Button } from 'react-bootstrap';

import ItemSearch from './ItemSearch';
import TransferCart from './TransferCart';

import '../css/styles.scss';

class TransferModal extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.handleShow = this.handleShow.bind(this);
    this.handleClose = this.handleClose.bind(this);

    this.state = {
      show: false
    };
  }

  handleClose() {
    this.setState({ show: false });
  }

  handleShow() {
    this.setState({ show: true });
  }

  render() {
    return (
      <div>
        <Button bsStyle="primary" bsSize="large" onClick={this.handleShow}>
          Transfer
        </Button>

        <Modal bsSize="large" show={this.state.show} onHide={this.handleClose}>
          <Modal.Header closeButton className="bg-slate-800">
            <Modal.Title className="text-center">Transfer Stock</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="col-md-5 transfer-cart-wrapper">
              <TransferCart />
            </div>
            <div className="col-md-7 transfer-products-wrapper">
              <ItemSearch />
            </div>
          </Modal.Body>
          <Modal.Footer >
            <Button className="mt-15" onClick={this.handleClose}>Close</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

export default TransferModal;
