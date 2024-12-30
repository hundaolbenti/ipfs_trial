// SPDX-License-Identifier: MIT

import './student.sol';
import './institute.sol';
pragma solidity ^0.8.0;

contract admin {
  address public MOE;

  constructor() {
    MOE = msg.sender;
  }

  modifier onlyMOE() {
    require(msg.sender == MOE);
    _;
  }
  // the moe verifies the institution which is only moe
  // institutions are pushed to an array
  // a student must be verified by one of the institutions in the array

  struct pendingStudents {
    string name;
    address student_address;
    string email;
    string id;
  }
  struct pendingInstitutes {
    string institute_name;
    address institute_address;
    string unique_id;
    address MOE_address;
  }

  mapping(address => address) registeredStudentsmap;
  mapping(address => address) registeredinstitutesmap;
  address[] registeredStudents;
  address[] registeredinstitutes;
  pendingStudents[] pendingStudentsarray;
  pendingInstitutes[] pendingInstitutesarray;

  function registerUsertopending(address Address, string memory Name, string memory email, string memory id, uint256 Role) public {
    if (Role == 1) {
      pendingStudents memory newpendingstudent;
      newpendingstudent.name = Name;
      newpendingstudent.student_address = Address;
      newpendingstudent.email = email;
      newpendingstudent.id = id;
      pendingStudentsarray.push(newpendingstudent);
    } else {
      pendingInstitutes memory newpendinginstitute;
      newpendinginstitute.institute_name = Name;
      newpendinginstitute.institute_address = Address;
      newpendinginstitute.unique_id = id;
      newpendinginstitute.MOE_address = MOE;
      pendingInstitutesarray.push(newpendinginstitute);
    }
  }

  // intitute verification my moe

  function verifyInstitution(uint256 _index) public onlyMOE {
    pendingInstitutes memory currentinst = pendingInstitutesarray[_index];
    institute newinst = new institute(currentinst.institute_name, currentinst.institute_address, currentinst.unique_id, currentinst.MOE_address);
    registeredinstitutesmap[currentinst.institute_address] = address(newinst);
    registeredinstitutes.push(currentinst.institute_address);
    delete pendingInstitutesarray[_index];
  }
  function verifyStudents(uint256 _index) public onlyverfiedInstitute {
    pendingStudents memory currentstudent = pendingStudentsarray[_index];
    student newstudent = new student(currentstudent.name, currentstudent.student_address, currentstudent.email, currentstudent.id);
    registeredStudentsmap[currentstudent.student_address] = address(newstudent);
    registeredStudents.push(currentstudent.student_address);
    delete pendingStudentsarray[_index];
  }

  function isStudent(address _studentAddress) public view returns (bool) {
    return registeredStudentsmap[_studentAddress] != address(0x0);
  }

  function isinstitutes(address _institutes) public view returns (bool) {
    return registeredinstitutesmap[_institutes] != address(0x0);
  }

  function StudentsCount() public view returns (uint256) {
    return registeredStudents.length;
  }

  function getStudentContractByAddress(address _employee) public view returns (address) {
    return registeredStudentsmap[_employee];
  }

  function institutesCount() public view returns (uint256) {
    return registeredinstitutes.length;
  }

  function getinstitutesContractByAddress(address _institutes) public view returns (address) {
    return registeredinstitutesmap[_institutes];
  }

  function isverified() public view returns (bool) {
    for (uint i = 0; i < registeredinstitutes.length; i++) {
      if (registeredinstitutes[i] == msg.sender) {
        return true;
      }
    }
    return false;
  }
  modifier onlyverfiedInstitute() {
    require(isverified(), 'You are not authorized!');
    _;
  }
}
